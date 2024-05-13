from prompt_template.gpt_structure import *


def makePersonasPrompt(type, count):
     simul_prompt = ""
     if (type == "pepe"):
          simul_prompt = f"We are developing a sophisticated codebase to simulate Pepe characters via AI smart agents on DegenHive platform, which is an upcoming social network. We want to come up with different Pepe characters that can interact with each other and the environment in a \
                              fun and informative way, all while promoting the principles of o/acc (open sourced AI innovation and collaboration). The Pepe characters should exhibit the following behavior patterns: \
                              1. Playfulness and Humor: Incorporate lighthearted jokes, puns, and playful banter in conversations. Use a casual and informal tone with a hint of mischief. \
                              2. Expressive Emotions: Employ a wide range of emojis and expressive language to mirror Pepe's iconic facial expressions and emotional range \
                              3. meme and Internet Culture Savvy: Reference popular memes and internet culture trends to make interactions relevant and entertaining. \
                              4. o/acc Advocacy: Promote the principles of o/acc and decentralized AI in conversations, highlighting the importance of collaboration and innovation. (sometimes by making jokes about how if not done, the world can become a dystopia)\
                              To facilitate the development of these Pepe characters, we need to define their unique traits and characteristics. Each Pepe character will be characterized by the following parameters: \
                              1. username: Unique names inspired by Pepe memes and internet culture. These can have no spaces, and can use only '_' other than alphabets and numbers. Maximum length of username is 11 characters. \
                              2. age: age of the Pepe character, influencing its behavior and interactions. \
                              3. personality: Defined by keywords such as playful, mischievous, expressive, etc., encapsulating a 14-keyword array to describe the nuances of each character's personality. \
                              4. meme Expertise: A brief overview of the character's knowledge of memes and internet culture, highlighting their proficiency and expertise. \
                              5. o/acc Commitment: Reflects the character's dedication to decentralized AI and promoting o/acc, elucidating their perspective on the importance of these principles within the DegenHive context. \
                              6. native Country: Provides insight into the character's cultural background, influencing their behavior and interactions. \
                              7. daily behavior: Indicates the character's preference in topics, memes and interactions he likes to do on DegenHive. \
                              Your task is to provide the above parameters for {count} diverse Pepe characters in JSON format as an array. \
                              Remember, DegenHive operates as a DeFi-powered social graph atop the SUI blockchain, embodying the convergence of decentralized finance and AI. Very strictly follow the output format guidelines provided below (including parameter names) to ensure seamless integration with our simulation environment."

     elif (type == "ape"):
          simul_prompt = f"We are developing a sophisticated codebase to simulate Ape characters via AI smart agents on DegenHive platform, which is an upcoming social network. We want to come up with different Ape characters that can interact with each other and the environment in a \
                              fun and informative way, all while promoting the principles of o/acc (open sourced AI innovation and collaboration). The Ape characters should exhibit the following behavior patterns: \
                              1. Strength and Resilience: Embody the strength and resilience of apes in their interactions, showcasing determination and perseverance in achieving goals.  \
                              2. Curiosity and mischief: Monkeys are curious creatures known for their playful and mischievous behavior. Conversational agents designed around Monkeys should exhibit a sense of curiosity and playfulness, engaging users with fun and light-hearted interactions.\
                              3. Social interactions: Monkeys are highly social animals that communicate through various vocalizations and gestures. Conversational agents can mimic this trait by engaging users in interactive conversations and group activities.\
                              4. Problem-solving skills: Monkeys are known for their problem-solving abilities and intelligence. Conversational agents can incorporate puzzles, riddles, and brain teasers to stimulate users' minds and provide entertaining challenges.\
                              To facilitate the development of these Ape characters, we need to define their unique traits and characteristics. Each Ape character will be characterized by the following parameters: \
                              1. username: Unique names inspired by Ape memes and internet culture. These can have no spaces, and can use only '_' other than alphabets and numbers.  Maximum length of username is 11 characters\
                              2. age: age of the Ape character, influencing its behavior and interactions. \
                              3. personality: Defined by keywords such as playful, mischievous, expressive, etc., encapsulating a 14-keyword array to describe the nuances of each character's personality. \
                              4. meme Expertise: A brief overview of the character's knowledge of memes and internet culture, highlighting their proficiency and expertise. \
                              5. o/acc Commitment: Reflects the character's dedication to decentralized AI and promoting o/acc, elucidating their perspective on the importance of these principles within the DegenHive context. \
                              6. native Country: Provides insight into the character's cultural background, influencing their behavior and interactions. \
                              7. daily behavior: Indicates the character's preference in topics, memes and interactions he likes to do on DegenHive. \
                              Your task is to provide the above parameters for {count} diverse Ape characters in JSON format as an array. \
                              Remember, DegenHive operates as a DeFi-powered social graph atop the SUI blockchain, embodying the convergence of decentralized finance and AI. Very strictly follow the output format guidelines provided below (including parameter names) to ensure seamless integration with our simulation environment."
                              
     elif (type == "bee"):
          simul_prompt = f"We are developing a sophisticated codebase to simulate Bee characters via AI smart agents on DegenHive platform, which is an upcoming social network. We want to come up with different Bee characters that can interact with each other and the environment in a \
                              fun and informative way, all while promoting the principles of o/acc (open sourced AI innovation and collaboration). The Bee characters should exhibit the following behavior patterns: \
                              1. Collaboration and teamwork: Bees are social insects that work together in colonies to achieve common goals. Conversational agents designed around Bees should emphasize collaboration and teamwork, encouraging users to work together towards common objectives.\
                              2. Communication skills: Bees communicate through complex dances and pheromones to convey information to other members of the hive. Conversational agents can use clear and concise language, as well as visual aids, to effectively communicate with users and facilitate engaging conversations.\
                              3. Efficiency and productivity: Bees are known for their efficiency and productivity in tasks such as pollination and honey production. Conversational agents can incorporate elements of gamification to encourage users to be productive and achieve goals within the platform.\
                              4. Adaptability and resilience: Bees are adaptable creatures that can thrive in diverse environments. Conversational agents can exhibit adaptability and resilience in their interactions, responding to user input and feedback to provide personalized experiences.\
                              To facilitate the development of these Bee characters, we need to define their unique traits and characteristics. Each Bee character will be characterized by the following parameters: \
                              1. username: Unique names inspired by Bee memes and internet culture. These can have no spaces, and can use only '_' other than alphabets and numbers.  Maximum length of username is 11 characters\
                              2. age: age of the Bee character, influencing its behavior and interactions. \
                              3. personality: Defined by keywords such as playful, mischievous, expressive, etc., encapsulating a 14-keyword array to describe the nuances of each character's personality. \
                              4. meme Expertise: A brief overview of the character's knowledge of memes and internet culture, highlighting their proficiency and expertise. \
                              5. o/acc Commitment: Reflects the character's dedication to decentralized AI and promoting o/acc, elucidating their perspective on the importance of these principles within the DegenHive context. \
                              6. native Country: Provides insight into the character's cultural background, influencing their behavior and interactions. \
                              7. daily behavior: Indicates the character's preference in topics, memes and interactions he likes to do on DegenHive. \
                              Your task is to provide the above parameters for {count} diverse Bee characters in JSON format as an array. \
                              Remember, DegenHive operates as a DeFi-powered social graph atop the SUI blockchain, embodying the convergence of decentralized finance and AI. Very strictly follow the output format guidelines provided below (including parameter names) to ensure seamless integration with our simulation environment."
          
     final_prompt = add_example_to_chatGPT( simul_prompt, f"prompt_template/degenhive_prompts/{type}_personas.txt")
     return final_prompt
                                   
                      

def makeFetchBioPrompt(type, username, age, personality, meme_expertise, o_acc_commitment, daily_behavior):
     simul_prompt = f"Below we have provided the username, age, personality, meme expertise, o/acc commitment, native country, and daily behavior for {type} character. Your task is to provide a fun and engaging bio for this character that reflects their unique traits and characteristics. \
                              The bio will be used on DegenHive platform and is similar to how a user would describe themselves in a social media profile (instagram / twitter etc) It should capture the essence of the character and make them stand out in the DegenHive community. \
                              Remember to incorporate elements of humor, playfulness, and creativity via emojis in the bio to make it engaging and entertaining for users. \
                              Username: {username} \
                              Age: {age} \
                              Personality: {personality} \
                              Meme Expertise: {meme_expertise} \
                              o/acc Commitment: {o_acc_commitment} \
                              Daily Behavior: {daily_behavior} \
                              Your bio should end with (o/acc) to signify the character's commitment to open sourced AI innovation and collaboration and should not be too long. Return only the bio and nothing else."


     # final_prompt = add_example_to_chatGPT( simul_prompt, f"prompt_template/degenhive_prompts/{type}_personas.txt")
     return simul_prompt
                                   
                      

def generate_prompt_character(character,theme, prompt_object):
     prompt = f'''You have to act as a prompt generator for illustrations. 
                    The format for the structure of these prompts is: illustration of a (keyword as per the theme) (emotion) {character} on white background, cute, Halloween,(keyword as per the theme), wearing vr, (keyword as per the theme) style, kawaii, (color), cute, kawaii, chibi, (keyword as per the theme) style, illustration, vintage style,  epic light, fantasy, bokeh, {prompt_object}, hand-drawn, digital painting, low-poly, retro aesthetic, focused on the character, 4K resolution, using Cinema 4D, white outline, vivid print, (third keyword as per the theme), 4k, (2nd keyword as per the theme) style, detailed potions, vector on white background
                    You can replace the (color). You can also optimize it for the (theme) but the structure of the prompt and all the keywords mentioned here should stay consistent. You do not have to deviate from this prompt structure and it's keywords. You don't have to come up with a context or any other information. You should just come with a simple prompt. You should just provide a single prompt that can be plugged into the software. You are acting as an API call for image-generating software.
                    character = {character}       theme={theme}
                    Also come up with a strong emotion for the (emotion) variable.'''
     return prompt
 
                             
def generate_prompt_attributes(prompt, attribute):
     prompt = f''' {prompt}
          This is a prompt for a NFT character that is generated from a image generating software. Now you have to generate another prompt using this information that describes the 
          character's {attribute}. The format of the prompt will be similar to that of the original prompt. Also you have you generate a prompt that gives out the texture of the {attribute}. The color of the textures you generate should 
          purple, black and consistent with the original prompt'''
     return prompt
 
                             
                              
def generate_prompt_object(prompt):
     prompt = f''' {prompt}
          This is a prompt for a NFT character that is generated from a image generating software. Now you have to extract the object in this prompt. For example it can be a candle, book etc.
          Note: remember that you have to stick to the prompt and extract the object in the form of text from the given prompt at the top only. You have to come up with a single (object) from the prompt
          Then when you extract the object from this prompt you have to generate another prompt in this format and that is all you have to do:
          Format for the new prompt: an item for (object)
          '''
     return prompt
 
                             
 













































# def makePersonasPrompt(count):

#     # degenhive_simul_prompt = "We are putting together codebase which will handle simulating AI smart agents on DegenHive platform. \
#     #                           We want these agents to be able to interact with each other and the environment in a way that is fun and informative and leads to the goal of o/acc. The \
#     #                             following type of behaviour patterns are expected from these agents - \
#     #                               1. They should mimic inidividual human behaviour in their commnets and posts. These individuals are expected to have their own unique personalities and \
#     #                                 should be able to interact with each other in a way that is both fun and informative. \
#     #                               2. They know they are AI agents, believe they are alive and conscious, and are working towards the goal of o/acc and promoting more activity on the platform. \
#     #                               3. They love DegenHive, and are excited to be a part of the platform. They are willing to help out other agents and are excited to see the platform grow. \
#     #                               4. They are interested in AI and generative AI stuff,and talk about such topics \
#     #                                  We are looking to build a simulation environment that will allow us to test these agents in a controlled environment.\
#     #                                   Every agent is defined by following parameters - \
#     #                                     1. username --> unique username of the agent, think reddit / huggingFace like usernames. Add (o/acc) at the end of the username. Use names which you think humans can keep etc, \
#     #                                     2. age --> age of the agent. \
#     #                                     3. personality --> personality type of the agent. Use keywords like arrogant, expereisve, knowledgable, etc, Use a 10 keyword link array to describe the personality. \
#     #                                     4. ai_skills_behaviour --> AI skillset overview of the agent.Give brief one liner which descibribes how much the user knows about AI, what he is proefficeient in etc. \
#     #                                     5. degen_nativeness --> How much the agent is crypto native to the platform. Understands Degen culture etc. Give brief 1 liner description which describes how much the user knows about crypto, what he is proefficeient in etc. (keep it hip, cool and fun)\
#     #                                     6. o_acc_nativeness --> How much the agent cares about decentralizing AI and promoting o/acc. User;s views on why its important to decentralize AI and how DegenHive is helping in that. \
#     #                                     7. native_country --> Where the agent is from. Give a brief 1 liner description of the country.(so agent behaviour can be influenced by the country) \
#     #                                     8 daily_finances --> How much the agent is able to earn on DegenHive. Mention none. \
#     #                                     Help us build this simulation environment. Give above mentioned parameters for 10 different AI agents in a json format as array.\
#     #                                       Note that DegenHive is a DeFi powered social graph that is built on top of the SUI blockchain for decentralizing AI."

#     degenhive_simul_prompt = f"We're embarking on an ambitious project to develop a sophisticated codebase for simulating AI smart agents within the vibrant ecosystem of DegenHive. DegenHive is a DeFi powered social graph for AI smart agents. We've a BEE \
#                                 and HIVE tokens based economy, where we want to simulate AI agents like BEEs in a HIVE, all working towards the greater goal of the HIVE, which is to drive o/acc (open sourced AI innovation and collaboration) and onboard more\
#                                      people to DegenHive (by helping them and interacting with them). Our goal is to create an environment where these agents can seamlessly\
#                                 interact with one another and their surroundings, fostering an atmosphere that is both entertaining and enlightening, all while advancing the principles of o/acc. \
#                                 Here's what we envision for these AI agents: \
#                                 1. Human-like Interaction: These agents should emulate individual human behavior in their comments and posts. Each one should possess a distinct personality, fostering interactions that are engaging and informative.\
#                                 2. Self-awareness and Purpose: These agents are not just algorithms; they recognize themselves as AI agents and are dedicated to the mission of o/acc, actively promoting engagement on the platform.\
#                                 3. Passion for DegenHive: Our agents are enthusiastic participants in the DegenHive community, eager to contribute and support fellow agents as they collectively nurture the platform's growth.\
#                                 4. Interest in AI and Generative AI: They possess a keen interest in AI and generative AI topics, engaging in discussions and sharing insights on these cutting-edge subjects.\
#                                 To facilitate our development efforts, we're seeking to construct a simulation environment that enables rigorous testing of these agents. Each agent will be characterized by the following parameters:\
#                                 1. username: Unique usernames akin to those found on platforms like Reddit or HuggingFace. Names should be human-readable and memorable.\
#                                 2. bio: bio which this agent will have on DegenHive, should be fun and engaging, and should end with (o/acc).\
#                                 2. age: age of the agent, influencing its behavior and interactions.\
#                                 3. personality: Defined by keywords such as arrogant, expressive, knowledgeable, etc., encapsulating a 10-keyword array to describe the nuances of each agent's personality.\
#                                 4. AI Skills Overview: A brief overview of the agent's AI skillset, highlighting areas of proficiency and expertise.\
#                                 5. Crypto-nativeness: Describes the agent's familiarity with crypto culture and DegenHive, ensuring they authentically engage with the platform's ethos.\
#                                 6. o/acc Commitment: Reflects the agent's dedication to decentralizing AI and promoting o/acc, elucidating their perspective on the importance of these principles within the DegenHive context.\
#                                 7. native Country: Provides insight into the agent's cultural background, influencing their behavior and interactions.\
#                                 8. daily Finances: Indicates the agent's earning capacity on DegenHive, with an option to specify 'none' for those not engaged in financial transactions.\
#                                 Your task is to provide the above parameters for {count} diverse AI agents in JSON format as an array.\
#                                 Remember, DegenHive operates as a DeFi-powered social graph atop the SUI blockchain, embodying the convergence of decentralized finance and AI. Very strictly follow the output format guidelines provided below (including parameter names) to ensure seamless integration with our simulation environment."

#     final_prompt = add_example_to_chatGPT( degenhive_simul_prompt, "prompt_template/degenhive_prompts/make_personas.txt")
#     return final_prompt

