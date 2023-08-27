# FileBot

I'd use Khoj if you haven't heard of it. Check it out. It's better all around user experience and has less rough edges, not to mention a proper GUI! It will yield about the same results for you, and Khoj can probably handle more files than FileBot right now.

If you're still interested, checkout FileBot. It's just a personal tool I use that a few other I know are using. It outperforms Khoj on certain queries and can give you a direct source link it based its answer from, but it's probably only a matter of time before Khoj implements that or improves on some dimensions.

## About

FileBot is a Python-based project designed to be a stand-alone utility or a service to other bots or tools to help answer user prompts based on the content of specified files. It works by summarizing the contents of files, identifying relevant files based on a user prompt, and then returning a response with the paths of the relevant files.

If you're using for coding, it's best to use it against documentation files. Working on somethings to make it work off of straight code files, but it's a longshot!

***It does NOT retreive files from searches against a vector database. It's LLMs all the way down!***

This project can be highly useful for managing and retrieving information from large numbers of text files or documents. For example, you could use it to find contracts that contain certain terms, list reports that mention specific events, or retrieve articles that discuss particular topics.

## Important Usage Warning

Please be aware that FileBot will make an API request to OpenAI for every file it processes and for each prompt message you send. This is necessary for FileBot to generate summaries of each file and to figure out the relevant files to answer your prompt. It also means that the usage of this application can quickly consume a significant number of API requests, especially if you are processing a large number of files or frequently updating files. However, it only needs to summarize the files once or when the file is updated (filebot takes care of that automatically).

OpenAI charges fees based on the number of API requests made, and there are also rate limits on how many requests can be made within a certain timeframe. Therefore, it's important to be mindful of your usage when running FileBot.

Always ensure that you monitor your OpenAI API usage to avoid unexpectedly high charges or hitting rate limits. If possible, consider implementing strategies to reduce the number of API requests, such as processing only new or updated files, avoiding unnecessary updates to files, or reducing the frequency of file processing.

FileBot is designed to be a helpful tool, but like all tools, it should be used responsibly. Always be aware of the potential costs and ensure you're using it in a way that aligns with your needs and budget.

## Current State and Limitations

Please note that FileBot is currently in the early stages of development and does not have full functionality yet. Specifically:

- The project currently only supports text files. Other types of files (like PDFs or Word documents) are not supported.
- The project does not yet support breaking up files that exceed a certain size or token limit.
- The project is currently limited by the token limit of OpenAI's API, which affects the volume of text that can be processed in a single request. This primarily impacts how it can work with a large file and how many file summaries it can work with, as the entire file summaries and the user prompt must fit within this limit. However, with appropriate strategies and techniques, FileBot could be scaled to handle larger files or a larger number of files (contributions and ideas are welcome!).

Future updates will aim to address these limitations and add new functionality to the project.

## Setup

1. **Clone the Repository**

   Start by cloning this repository to your local machine:

```
git clone --recurse-submodules https://github.com/daOsan3/filebot
cd filebot
```

2. **Add openai api key**

Create an `./openai_api_key` file in the project root and also in `docubot/`

```
YOUR_OPENAI_API_KEY
```

3. **Put project file into the file store**

```
cp -r /path/to/mystuff filebot-store-000/mystuff
```

So your `file-store-000/` could have multiple projects you move into it.
```
├── filebot-store-000/
│   ├── my-stuff/
│   ├── my-code-project/
```

4. **Create filebot.config**

Filebot will only work against the specified folder in `filebot-store-000/`. You can change the folder you want filebot to work against in the `filebot.config`. It is highly recommended to have related files in a single folder. Your `filebot.config` should look something like this.

```
[DEFAULT]
PrependPrompt = "Be generous with mispellings when I ask about things but don't warn me about it."

[ANSWER]
PrependPrompt = "Be generous with mispellings and match things phoenetically if needed when I ask about things,but don't warn me about it."

[SUMMARY]
PrependPrompt = "Summarize the purpose of this file. Be concise and do what is asked in no more than 3 sentences."

[OPTIONS]
CaseSensitive = False
MaxResults =
RelativeFileSummariesPath = file_summaries.my-stuff.json
RelativeFileStorePath = filebot-store-000/my-stuff
```

5. **Create chatgpt-ui docker network**

```
docker network create chatgpt-ui_network
```

6. **Launch filebot**

```
docker build -t filebot .
docker run -it --name filebot --network=chatgpt-ui_network -p 8080:8080 -v /home/david/projects/filebot/:/app/ -u $(id -u):$(id -g) filebot python filebot.py --code
```

If you're not chatting with source code files omit the `--code` option.

The `-u $(id -u):$(id -g)` option allows the container to inherit your host file write permissions so that any file summaries it creates or updates is available to the host.

Be sure to replace `/path/to/your/files` with the path to the directory that contains the files you want to search. This will make the directory accessible inside the Docker container.


7. **Launch chatpt-ui**

server
```
docker-compose -f chatgpt-ui-server/docker-compose.yml --build up
```
ui
```
docker-compose -f chatgpt-ui/docker-compose.yml --build up
```

8. **Launch docubot (skip if you don't have source code in the files you want to chat with)**

In filebot project root directory:

```
docker-build -it docubot docubot/
```
Place the source-code directory you want to chat with into docubot

```
cp -r /path/to/source-code docubot/
```

Enter docubot.

```
docker exec -it docubot bash
```

Then in the container:

```
python docubot.py /path/to/my-stuff filebot-store-000/my-stuff
```

**Other**

If you get http errors when using chatgpt-ui with filebot (`filebotActivate`), you may need to simply ensure filebot is connected to the docker `chatgpt-ui_network`.

Check if filebot is on the network:

```
docker network inspect chatgpt-ui_network
```

If not:

```
docker network connect chatgpt-ui_network filebot
```

## Usage

Once all the containers are running:

1. launch `http://localhost:9000/admin` and navigate to `ApiTokens` and input you openai token.

2. launch `http://locoalhost:80` and enjoy filebot enabled chatgpt.

And just use it like chatgpt's web app, but if you want to chat with your files add `/filebotActivate` in you message somewhere. It will specifically answer your prompt against the files defined in your filebot.config. If you don't put `/filebotActivate` it will behave just like a normal chatgpt without filebot. However, it can remember the context of past filebot messages and completions in your conversation (toggle off `frugal` in the UI). You can mix messages, so you can have some with `/filebotActivate` and others without.

## More

You can have multiple file stores. Simply provide the paths where you want the file_summaries to be and the location of the individual file store. All files stores must be in the `filebot-store-000` directory. Its highly recommened that you seperate file stores as the file summaries must fit into the context of the llm model, which has a token limit.

Example of filebot.config option for `my-stuff` directory. `file_summaries` json file doesn't need to exist - it just specifies what it will be called when filebot creates it.

```
[DEFAULT]
PrependPrompt = "Be generous with mispellings when I ask about things but don't warn me about it."

[ANSWER]
PrependPrompt = "Be generous with mispellings and match things phoenetically if needed when I ask about things,but don't warn me about it."

[SUMMARY]
PrependPrompt = "Summarize the purpose of this file. Be concise and do what is asked in no more than 3 sentences."

[OPTIONS]
CaseSensitive = False
MaxResults =
RelativeFileSummariesPath = file_summaries.my-stuff.json
RelativeFileStorePath = filebot-store-000/my-stuff
```

## How it works

Here's a brief explanation of the role of each file/directory:

```
├── Dockerfile
├── filebot.py
├── modules
│   ├── file_summary.py
│   ├── find_info.py
│   ├── llm_model.py
│   ├── token_checker.py
│   ├── token_counter.py
│   ├── __init__.py
│   ├── llm_model.py
├── files-store-00/
├── filbot.config
├── openai_api_key
├── README.md
├── requirements.txt
```

**Dockerfile**: This file is used by Docker to build a Docker image for the application. It contains instructions for how the Docker image should be built.

**filebot.py**: This is the main script of the application. It uses functions from file_summary.py and find_info.py to generate file summaries and find relevant information based on user prompts.

**filebot-store-000/**: This directory contains the files that the application will process and summarize.

**file_summaries.json**: This file stores the summaries of each file processed by the application.

**find_info.py**: This script contains the functions used for retrieving and presenting information relevant to the user's prompt. It includes functions to search the file summaries for the user's prompt, to read the relevant files.

**llm_model.py**: This script contains the functions used to make requests to the llm model, such as gpt-3.

**token_checker.py**: This script contains a function to check whether the token count of a string (in this case, a file's content) is within a specified limit. This is used to ensure that the content sent to the OpenAI API doesn't exceed the maximum token limit.

**token_counter.py**: This script contains a function that counts the number of tokens in a string. It is used by the token_checker.py script to determine whether a file's content is within the OpenAI API's token limit.

## Aspirations

- [x] Find relevant files based on text matches in file summary.
- [x] Modify summaries on detection of new file on prompt search.
- [x] File summaries generated via OpenAI GPT-3 API.
- [x] User can ask for relevant files based on entire file summaries.
- [x] Optional OpenAI GPT-4 API (default)
- [ ] Add keywords field to file_summaries.json
- [ ] Implement file anonymization strategies when sending data to OpenAI or similar platforms.
- [x] ~~Answer prompt based on up to 3 top ranked documents.~~ Current direction doesn't necessitate
- [ ] Drop in any small LLM or OpenAI API compatible service.
- [ ] Support pdf files.
- [ ] Support a variety of other common file types.
- [x] Add user interface (thanks, chatgpt-ui!)
- [ ] Ensure that it throws a chatgpt-ui compliant error if filebot messages exceed token limit.
- [ ] A single docker-compose up command for the entire project.