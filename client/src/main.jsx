import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { Providers } from "@microsoft/mgt-element";
import { Msal2Provider } from "@microsoft/mgt-msal2-provider";


Providers.globalProvider = new Msal2Provider({
    clientId: 'feabfea1-587f-47f4-a7fe-2156fffe12b1'
  });

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
