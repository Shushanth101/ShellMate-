const { Type } = require('@google/genai')

const executeCommandFunctionDeclaration = {
  name: 'executeCommand',
  description: 'Executes a shell-style command given as a single string.',
  parameters: {
    type: Type.OBJECT,
    properties: {
      command: {
        type: Type.STRING,
        description: 'The full command string to execute (e.g., "cat filename.txt", "ls", "mkdir dirname").',
      },
    },
    required: ['command'],
  },
};

const readFileFunctionDeclaration = {
  name: "read_file",
  description: "Reads the contents of a file and returns it as a string.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      path: {
        type: Type.STRING,
        description: "The relative path of the file to read (e.g., 'folder\\\\file.txt')"
      }
    },
    required: ["path"]
  }
}

const writeToFileFunctionDeclaration = {
  name: "write_to_file",
  description: "Writes given content to a file at the specified path.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      path: {
        type: Type.STRING,
        description: "The file path where the content should be written."
      },
      content: {
        type: Type.STRING,
        description: "The content to write into the file."
      }
    },
    required: ["path", "content"]
  }
};

const searchFilesFunctionDeclaration = {
  name: "searchFiles",
  description: "Recursively searches for files in a directory whose names include the given keyword.",
  parameters: {
    type: Type.OBJECT,
    properties: {
      dir: {
        type: Type.STRING,
        description: "The root directory where the search should begin."
      },
      keyword: {
        type: Type.STRING,
        description: "The keyword to look for in file names."
      },
      excludeDirs: {
        type: Type.ARRAY,
        items: { type: Type.STRING },
        description: "List of directory names to skip during the search."
}
    },
    required: ["dir", "keyword"]
  }
};


const googleSearchFunctionDeclaration = {
  name: "googleSearch",
  description: "Searches the web using the Google Custom Search API.",
  parameters: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "The search query string to look up on Google.",
      },
    },
    required: ["query"], 
  },
};




module.exports = {
    executeCommandFunctionDeclaration,
    readFileFunctionDeclaration,
    writeToFileFunctionDeclaration,
    searchFilesFunctionDeclaration,
    googleSearchFunctionDeclaration
}
