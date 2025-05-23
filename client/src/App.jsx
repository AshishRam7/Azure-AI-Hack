import React, { useState, useRef, useEffect } from 'react';
// import './chatbot.css';
import './App.css'
import MicrosoftLogin from "react-microsoft-login";
// import Appnew from './Auth';
import { PublicClientApplication } from "@azure/msal-browser";
import { Login } from '@microsoft/mgt-react';


const BotIcon = () => <div className="avatar">🤖</div>;
const UserIcon = () => <div className="avatar">👤</div>;
const SendIcon = () => <>➡️</>;
const ThemeIcon = () => <>🔄</>;


const App = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState('dark');
  const messagesEndRef = useRef(null);
  const [steps,setsteps] = useState([]);
  const clientid = "feabfea1-587f-47f4-a7fe-2156fffe12b1"


const msalConfig = {
  auth: {
    clientId: 'feabfea1-587f-47f4-a7fe-2156fffe12b1',
    redirectUri: 'http://localhost:3000',
    authority: 'https://login.microsoftonline.com/152bb883-12c5-48cd-b76c-6b7509cb478e',
  },
};



  // Themes configuration
  const themes = ['dark', 'light', 'ocean', 'forest'];

  // Cycle through themes
  const cycleTheme = () => {
    const currentIndex = themes.indexOf(theme);
    const nextIndex = (currentIndex + 1) % themes.length;
    setTheme(themes[nextIndex]);
  };

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // API call function
  const fetchResponse = async (question) => {
    try {
      setIsLoading(true);
      const response = await fetch('https://ms-deploy-mcp.onrender.com/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          messages: [
            {
              "role": "user",
              "content": question
            }
          ]
        })
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const data = await response.json();
      return {txt:data.reply,steps:data.messages }|| 'Sorry, I could not process your request.';
    } catch (error) {
      console.error('Error:', error);
      return 'Sorry, there was an error processing your request.';
    } finally {
      setIsLoading(false);
    }
  };
  
  // Handle message submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    const userMessage = { 
      id: Date.now(), 
      text: trimmedInput, 
      type: 'user' 
    };
    setMessages(prev => [...prev, userMessage]);

    setInput('');

    const aiResponse = await fetchResponse(trimmedInput);
    
    const aiMessage = { 
      id: Date.now() + 1, 
      text: aiResponse.txt, 
      steps: aiResponse.steps,
      type: 'ai' 
    };
    console.log("this ois",aiResponse.steps)
    setMessages(prev => [...prev, aiMessage]);
  };
  const authHandler = (err, data) => {
    console.log("hey this",err, data);
  };

  
  const handleLogin = async () => {
    const msalInstance = new PublicClientApplication({
      auth: {
        clientId: "feabfea1-587f-47f4-a7fe-2156fffe12b1", // Replace with your app's client ID
        authority: "https://login.microsoftonline.com/152bb883-12c5-48cd-b76c-6b7509cb478e", // Replace with your tenant ID
        redirectUri: "http://localhost:3000",
      },
    });


    try {
      // Login the user
      await msalInstance.loginPopup({
        scopes: ["user.read", "mail.read"],
      });

      // Acquire access token silently
      const result = await msalInstance.acquireTokenSilent({
        scopes: ["user.read", "mail.read"],
      });

      console.log("Access Token:", result.accessToken);
    } catch (err) {
      console.error("Authentication error:", err);
    }
  };
  const key = Object.keys(localStorage).find(k => k.includes("accesstoken"));
  const tokenObj = JSON.parse(localStorage.getItem(key));
  console.log("Access Token:", tokenObj.secret);
  

  return (
    <div>
 <div className="app">
     <header>
       <Login />
     </header>
   </div>    </div>
//     <div className={`chatbot-container theme-${theme}`}>
//       {/* Header with Theme Toggle */}
//       <div className="chatbot-header">
//         <h1>
//           <BotIcon />
//           AIssistMail
//         </h1>
//         <button 
//           onClick={cycleTheme} 
//           className="theme-toggle"
//           title="Change Theme"
//         >
//           <ThemeIcon />
//         </button>
//       </div>

//       {/* Messages Container */}
//       <div className="messages-container">
//         {messages.map((message) => (
//           <div 
//             key={message.id} 
//             className="message-container"
//             style={{ 
//               flexDirection: message.type === 'user' ? 'row-reverse' : 'row' 
//             }}
//           >
//             {message.type === 'ai' ? <BotIcon /> : <UserIcon />}
            
//             <div 
//               className={`message ${
//                 message.type === 'user' ? 'message-user' : 'message-ai'
//               }`}
//             >
//               {message.steps && message.steps.length > 0 && (
//   <div className="steps-container">
//     <h2>Message Steps:</h2>
//     {message.steps.map((step, index) => (
//       <div key={index} className="step-message">
//         <strong>Step {index + 1}:</strong> {step.role}: {step.content}
//       </div>
//     ))}
//   </div>
// )}
//   <div className={`message ${
//                 message.type === 'user' ? 'message-user' : 'message-ai'
//               }`}>
//     <h3>{message.text}</h3>
//   </div>

//             </div>
//           </div>
//         ))}

//         {/* Loading Indicator */}
//         {isLoading && (
//           <div className="loading-indicator">
//             <BotIcon />
//             <div className="loading-text">Thinking...</div>
//           </div>
//         )}

//         {/* Scroll Anchor */}
//         <div ref={messagesEndRef} />
//       </div>

//       {/* Input Area */}
//       <form 
//         onSubmit={handleSubmit} 
//         className="input-area"
//       >
//         <input 
//           type="text" 
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask me anything..."
//         />
//         <button 
//           type="submit" 
//           disabled={!input.trim() || isLoading}
//         >
//           <SendIcon />
//         </button>
//       </form>
//     </div>
  );
};

export default App;