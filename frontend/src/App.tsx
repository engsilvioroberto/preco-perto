
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { Search } from './pages/Search';
import { Map } from './pages/Map';
import { Scan } from './pages/Scan';
import { Profile } from './pages/Profile';
import { Admin } from './pages/Admin';
import './App.css';

function App() {
  return (
    <Router basename="/preco-perto">
      <div className="app">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/search/:productId" element={<Search />} />
          <Route path="/map/:productId" element={<Map />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
