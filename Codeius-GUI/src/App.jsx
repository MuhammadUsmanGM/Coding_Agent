import './App.css'
import Navbar from './components/Navbar/Navbar'
import InputField from './components/InputField/InputField'
import Sidebar from './components/Sidebar/Sidebar'

function App() {
  return (
    <div className="App">
      <Navbar />
      <Sidebar />
      {/* The background image remains visible as the background of the App div */}
      <InputField />
    </div>
  )
}

export default App
