/**
 * Home Page
 * 
 * Main page component. Currently displays component tests for development.
 * Switch between different test components to verify functionality:
 * - TailWindTest: Color palette verification
 * - MessageBubbleTest: MessageBubble component testing
 * - MessageInputTest: MessageInput component testing
 * - ComponentTests: Combined interactive test
 */
// import ComponentTests from '@/components/ComponentTests'
// import TailWindTest from '@/components/TailwindTest'
// import MessageBubbleTest from '@/components/MessageBubbleTest'
// import MessageInputTest from '@/components/MessageInputTest'
import MessageListTest from "@/frontend_testing/MessageListTest";
// import ChatWindow from "@/components/ChatWindow";
 import ChatWindowTest from "@/frontend_testing/ChatWindowTest";
import ChatWindow from "@/components/ChatWindow";
import { Message } from '@/types';
import { useState } from 'react';
import UseChatTest from "@/frontend_testing/useChatTest";
import ApiTest from "@/frontend_testing/apiTest";
import UseChatTestReal from "@/frontend_testing/useChatTestReal";
export default function Home() {
  // Uncomment the test component you want to see:
  // return <ApiTest />
  return <UseChatTestReal />
  // return <UseChatTest />
  // State to store messages for the chat
  // const [messages, setMessages] = useState<Message[]>([]);
  // // State to simulate loading/agent response generation
  // const [isLoading, setIsLoading] = useState(false);
  // // Counter for generating unique message IDs
  // const [messageCounter, setMessageCounter] = useState(0);
    /**
   * Handles message sending from ChatWindow
   * Simulates sending a user message and generating an agent response
   * 
   * @param messageText - The message text sent by the user
   */
//   const handleSendMessage = (messageText: string) => {

//     // Create user message object
//     const userMessage: Message = {
//       id: `user-${messageCounter}`,
//       message: messageText,
//       sender: 'user',
//       timestamp: new Date().toISOString(),
//     };

//     // Add user message to the message list
//     setMessages((prev) => [...prev, userMessage]);
//     setMessageCounter((prev) => prev + 1);

//     // Simulate agent response generation
//     setIsLoading(true);
    
//     // Simulate agent thinking/generating response (with delay)
//     setTimeout(() => {
//       // Create agent response message
//       const agentMessage: Message = {
//         id: `agent-${messageCounter}`,
//         message: `Thank you for your message: "${messageText}". This is a simulated agent response. I'm here to help you with any questions you might have.`,
//         sender: 'agent',
//         timestamp: new Date().toISOString(),
//       };
      
//       // Add agent message to the message list
//       setMessages((prev) => [...prev, agentMessage]);
//       setMessageCounter((prev) => prev + 1);
      
//       // Stop loading state
//       setIsLoading(false);
//     }, 2000);
// };

//   return <ChatWindow 
//   messages={[]}
//   onSendMessage={handleSendMessage}
//   isLoading={isLoading}
//   agentName="Support Agent"
//   />
}
