import logo from './logo.svg';
import './normal.css';
import './App.css';
import { useState, useRef } from 'react';
import Modal from 'react-modal';
import axios from 'axios';

function App() {
  const [windowSize, setWindowSize] = useState([
    window.innerWidth,
    window.innerHeight,
  ]);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  // add state for input and chat log
  const [input, setInput] = useState("");
  // const apiUrl = process.env.REACT_APP_API_URL;
  const apiUrl = 'http://localhost:5000';
  // const apiUrl = "http://csc.csilabs.eu:5000";

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [server, setServer] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [wazuhTestResult, setWazuhTestResult] = useState('');

  const fetchConfig = async () => {
    try {
      const response = await axios.get(apiUrl + '/api/config');
      const configData = response.data;
      setServer(configData.server);
      setUsername(configData.username);
      setPassword(configData.password);
    } catch (error) {
      console.error('Error fetching configuration:', error);
    }
  };

  const openModal = () => {
    setIsModalOpen(true);
    setWazuhTestResult('');
    fetchConfig();
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const testConfiguration = () => {
    setWazuhTestResult("Successfully connected to wazuh server");
  }

  const saveConfiguration = () => {
    console.log('Server:', server);
    console.log('Username:', username);
    console.log('Password:', password);

    const config = {
      server: server,
      username: username,
      password: password,
    };
  
    axios.post(apiUrl + "/api/config", config)
      .then(response => {
        console.log('Configuration saved:', response.data);
        closeModal();
      })
      .catch(error => {
        console.error('Error saving configuration:', error);
      });
  };

  const [chatLog, setChatLog] = useState([
    // {
    //   user: "gpt",
    //   message: "Hi, I am \"THOR-HUNT Pro\", a smart cybersecurity assistant. You can query the data easier and in convenient way. What wou can do now is asking about the IP reported through a specific date, or get the latest updates from different tiers such as twitter, community feed, or crawled web."
    // }
    // {
    //   user: "me",
    //   message: "Hi, give me details of the reported IP addresses on 27th of march 2023."
    // },
    // {
    //   user: "gpt",
    //   message: "There are 977 reported IP addresses. 864 of them are reported from Community Feeds, and the rest from Twitter and Craweled Web."
    // },
    // {
    //   user: "me",
    //   message: "Is this IP reported: 27.210.32.226"
    // },
    // {
    //   user: "gpt",
    //   message: "I cannot find this IP in Elasticsearch"
    // }
  ]);

  async function handleSubmit(e){
    e.preventDefault();
    addDialog(input, "me");
    setInput("");
    // await new Promise((resolve) => setTimeout(resolve, 500));
    // addDialog("I am thinking", "gpt")
    var responseMessage = await getResponse(input);
    addDialog(responseMessage, "gpt")
  }

  async function addDialog(input, role){
    console.log(input)
    setChatLog(chatLog => [...chatLog, { user: role, message: `${input}`}]);
    console.log(chatLog)
    scrollToBottom();
  }

  async function getResponse(input){
    // Make the POST request
    const response = await fetch(apiUrl + "/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({"message": input}),
    });

    if (response.ok) {
      const responseData = await response.json();
      console.log(responseData)
      // Update the chat log with the response data
      return responseData.message;
    } else {
      console.error("Failed to make the POST request.");
    }
  }

  return (
    <div className="App">
      <aside className="sidemenu">
      <div onClick={openModal} className="sidemenu-button configuration-button">
          <span></span>
          Configuration
        </div>
        <br></br>
        <div className="sidemenu-button">
          <span>+</span>
          New Chat
        </div>
        <div className="sidemenu-history">
          <span className='title'>History</span>
          <div className="history-item">
            <span className='date'>08 Jun 2023</span>&nbsp;-&nbsp; 
            <span className='text'>IP search</span>
          </div>
          <div className="history-item">
            <span className='date'>08 Jun 2023</span>&nbsp;-&nbsp; 
            <span className='text'>IP search</span>
          </div>
        </div>
      </aside>
      <section className="chatbox">
        <div className="chat-log">
          { chatLog.map((message, index) => (
              <ChatMessage key={index} message={message}/>
          ))}
          <div className="chat-bottom" ref={messagesEndRef}>
          </div>
        </div>
        <div className="chat-input-holder">
          <form onSubmit={handleSubmit}>
            <input 
              rows="1"
              value={input}
              onChange={e => setInput(e.target.value) }
              className="chat-input-textarea">
            </input>
          </form>
        </div>
      </section>
      <div>
      <Modal
        isOpen={isModalOpen}
        style={{
          overlay: {
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          },
          content: {
            backgroundColor: '#282c34',
            border: 'none',
            borderRadius: '10px',
            maxWidth: '400px',
            margin: 'auto',
            padding: '20px',
            height: '50vh'
          },
        }}
      >
          <h2 className="modal-title">Configuration</h2>
          <hr/>
          <h4 className="modal-title">Wazuh Configuration</h4>
          <input
            type="text"
            placeholder="Server"
            value={server}
            onChange={(e) => setServer(e.target.value)}
            className="modal-input"
          />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="modal-input"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="modal-input"
          />
          <span className='modal-message'>{wazuhTestResult}</span>
          <div className="modal-button-container">
            <button onClick={testConfiguration} className="modal-button test-button">
              Test Connection
            </button>
            <button onClick={saveConfiguration} className="modal-button save-button">
              Save
            </button>
            <button onClick={closeModal} className="modal-button cancel-button">
              Cancel
            </button>
          </div>
        </Modal>
      </div>
    </div>
  );
}

const ChatMessage = ({message}) => {
  return(
    <div className={`chat-message ${message.user === "gpt" && "chatgpt"}`}>
      <div className="chat-message-center">
        <div className={`avatar ${message.user === "gpt" && "chatgpt"}`}>
        </div>
        <div className="message">
        {message.message}
        </div>
      </div>
    </div>
  )
}

export default App;
