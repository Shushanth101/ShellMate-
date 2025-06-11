#!/usr/bin/env node
const  { GoogleGenAI, Type } = require('@google/genai');
const { executeCommandFunctionDeclaration,readFileFunctionDeclaration,writeToFileFunctionDeclaration,searchFilesFunctionDeclaration,googleSearchFunctionDeclaration } = require('./functiondeclarations')
const { executeCommand,read_file,write_to_file,searchFiles,googleSearch } = require('./tools')
const SYSTEM_PROMPT = require('./systeminstruction')
const readline = require('readline');

const GEMINI_API_KEY = "AIzaSyAAbrWaKJ3JJmo1owXKqHNfYSlERIDRDd4"


// Configure the client
const ai = new GoogleGenAI({ apiKey: GEMINI_API_KEY });

const TOOL_MAP = {
    "executeCommand" :executeCommand,
    "read_file":read_file,
    "write_to_file":write_to_file,
    "searchFiles":searchFiles,
    "googleSearch":googleSearch
}






async function init() {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  const chat = await ai.chats.create({
    model: 'gemini-2.0-flash',
    config: {
      systemInstruction: SYSTEM_PROMPT,
      tools: [{ functionDeclarations: [executeCommandFunctionDeclaration,readFileFunctionDeclaration,writeToFileFunctionDeclaration,googleSearchFunctionDeclaration,searchFilesFunctionDeclaration] }],
    },
  });

  const promptUser = () => {
    rl.question('\n> ', async (userInput) => {
      if (userInput.toLowerCase() === 'exit' || userInput.toLowerCase() === 'quit') {
        rl.close();
        console.log('👋 Exiting...');
        return;
      }

      try {
        let response = await chat.sendMessage({ message: userInput });

        while (response.functionCalls && response.functionCalls.length > 0) {
          const functionCall = response.functionCalls[0];
          const functionToCall = functionCall.name;
          const args = functionCall.args;

          console.log(`\nFunction to call: ${functionToCall}`);
          console.log(`Arguments: ${JSON.stringify(args)}`);

          if (TOOL_MAP[functionToCall]) {
            const toolResponse = await TOOL_MAP[functionToCall](args);
            console.log(`Tool response: ${toolResponse}`);

            // Send result back to Gemini and get its next response
            response = await chat.sendMessage({ message: `ToolResponse: ${toolResponse}` });
          } else {
            console.error(`No tool found for "${functionToCall}"`);
            response = await chat.sendMessage({
              message: `Tool "${functionToCall}" is not available.`,
            });
          }
        }

        // Final model reply (after any function calls)
        if (response.text) {
          console.log(`🤖 Gemini: ${response.text}`);
        }
      } catch (error) {
         await chat.sendMessage({message:`Error: ${error}`})
        console.error('Error during chat:', error);
       
      }

      promptUser();
    });
  };

  console.log('💬 Start chatting with Gemini! (type `exit` to quit)');
  promptUser();
}


init()
