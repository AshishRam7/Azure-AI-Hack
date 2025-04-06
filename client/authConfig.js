export const msalConfig = {
    auth: {
      clientId: "feabfea1-587f-47f4-a7fe-2156fffe12b1", 
      authority: "https://login.microsoftonline.com/common", 
      redirectUri: "http://localhost:3000",
    },
    cache: {
      cacheLocation: "localStorage",
      storeAuthStateInCookie: false,
    },
  };
  
  export const loginRequest = {
    scopes: ["User.Read"],
  };
  