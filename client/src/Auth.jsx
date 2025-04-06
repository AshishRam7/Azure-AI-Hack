import React, { useState } from "react";
import { PublicClientApplication } from "@azure/msal-browser";

 const msalInstance = new PublicClientApplication({
      auth: {
        clientId: "feabfea1-587f-47f4-a7fe-2156fffe12b1", // Replace with your app's client ID
        authority: "https://login.microsoftonline.com/152bb883-12c5-48cd-b76c-6b7509cb478e", // Replace with your tenant ID
        redirectUri: "http://localhost:3000",
      },
    });

const LoginButton = () => {
  const [isInitialized, setIsInitialized] = useState(false);

  const handleLogin = async () => {
    try {
      if (!isInitialized) {
        await msalInstance.initialize();
        setIsInitialized(true);
      }
  
      // Login popup
      const loginResponse = await msalInstance.loginPopup({
        scopes: ["user.read", "mail.read"],
      });
  
      // ✅ Set active account
      msalInstance.setActiveAccount(loginResponse.account);
  
      // Now you can acquire the token silently
      const result = await msalInstance.acquireTokenSilent({
        scopes: ["user.read", "mail.read"],
        account: loginResponse.account, // optional now that active account is set
      });
  
      console.log("Access Token:", result.accessToken);
    } catch (err) {
      console.error("Authentication error:", err);
    }
  };
  

  return (
    <button
      onClick={handleLogin}
      style={{
        padding: "10px 20px",
        borderRadius: "6px",
        backgroundColor: "#0078D4",
        color: "#fff",
        border: "none",
        cursor: "pointer",
        fontSize: "16px",
      }}
    >
      Sign In with Microsoft
    </button>
  );
};

export default LoginButton;
