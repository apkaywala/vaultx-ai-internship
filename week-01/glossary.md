Week-01- AI-Terminology Glossary

1: Token: Token is a small chunk of text that a language model reads or generates.
   It is sometimes a word or a single punctuation mark

2: Context Window: Context window is the maximum amount of text that a model can see at once.
   It includes prompts or system instructions

3: Temperature: Temperature shows that how random or predictable the models's word choices are.
   Low temperature model gives predictable answers.
   High temperature models give unpredictable answers with randomness.

4: Top-P: Top-p controls the range of possible word choices the AI can consider when generating text. 
   Low top-p considers fewer, more likely words, more predictable answers.
   High top-p considers more possible words, more varied answers.

5: System Prompt: A system prompt is a set of instructions given to a model before the users's actual message.
   It tells the AI how to behave, its tone, rules or constraints.

6: Embedding: Embedding is way of turning text images or other data into numbers so the AI model can understand relationship between them.
   "I love cats" & "Cats are my favorite animals" both are two different sentences with same meaning so the vectors for both would be close to each other

7: Hallucination: A hallucination is when a model generates information that sounds fluent and conident but according to facts
   it is wrong or entirely madeup.

8: Fine-Tunning: Fine-Tunning is training of an already trained AI model over a specific dataset so it
   could become better at that specific task.

9: Inference: Inference is the act of running a trained model to get some output by giving it some input.
   Every time we send a prompt and recieve a response it is called inference call.

	 >>Difference Between Base model and Instruction tuned model<<
Base Model: Base model is trained to predict next token/word.
it has general knowledge but isn't trained to follow user instructions.

Instruction Tuned Model : Instruction tuned model is model that is specially designed to follow user instructions

         >>Why an LLM Predicts Text Rather Than "Knows" Facts

An LLM is trained to predict the most statistically likely next token given everything before it, not to 
store or look up verified facts the way a database does. Its "knowledge" is really just patterns learned 
from the text it was trained on, compressed into billions of numerical weights, with no built-in mechanism
 to check what's actually true
