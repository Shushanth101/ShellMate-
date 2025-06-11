const { exec } = require("child_process");
const fs = require("fs").promises;
const path = require("path");
const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();

const executeCommand = (commandObject) => {
  return new Promise((resolve, reject) => {
    exec(commandObject.command, (error, stdout, stderr) => {
      if (error) {
        return reject(
          `Failed to execute: "${commandObject.command}"\nError: ${error.message}\nStderr: ${stderr}`
        );
      }
      resolve(
        `Executed: "${commandObject.command}"\nStdout:\n${stdout || "None"}\nStderr:\n${stderr || "None"}`
      );
    });
  });
};


const read_file = async ({ path }) => {
  try {
    const contents = await fs.readFile(path, "utf-8");
    return contents;
  } catch (error) {
    return `Failed to read file at "${path}": ${error.message}`;
  }
};


const write_to_file = async ({ path, content }) => {
  try {
    await fs.writeFile(path, content, "utf-8");
    return `Successfully wrote to file: ${path}`;
  } catch (error) {
    return `Failed to write to file "${path}": ${error.message}`;
  }
};


const searchFiles = async ({ dir, keyword, excludeDirs = [], baseDir = dir }) => {
  const results = [];
  try {
    const files = await fs.readdir(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = await fs.stat(fullPath);

      if (stat.isDirectory()) {
        if (excludeDirs.includes(file)) continue;
        const subResults = await searchFiles({ dir: fullPath, keyword, excludeDirs, baseDir });
        results.push(...subResults);
      } else if (file.includes(keyword)) {
        results.push(path.relative(baseDir, fullPath)); 
      }
    }
  } catch (error) {
    console.error(`Error searching in ${dir}:`, error.message);
  }
  return results;
};



const googleSearch = async ({ query }) => {
  try {
    const response = await axios.get("https://www.googleapis.com/customsearch/v1", {
      params: {
        key: process.env.GOOGLE_SEARCH_API,
        cx: process.env.SEARCH_ENGINE_ID,
        q: query,
      },
    });

    const results = (response.data.items || []).slice(0, 5).map((result) => ({
      title: result.title,
      htmlTitle: result.htmlTitle,
      link: result.link,
      snippet: result.snippet,
    }));

    return results;
  } catch (error) {
    console.error("Google Search API Error:", error.response?.data || error.message);
    return [];
  }
};

module.exports = {
  executeCommand,
  read_file,
  write_to_file,
  searchFiles,
  googleSearch,
};



