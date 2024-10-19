import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {login} from "../services/Auth";
const LoginPage = () => {
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      // Call the login function from auth service
      const data = await login(identifier, password);

      // Save the token in localStorage
      localStorage.setItem('token', data.access_token);

      // Redirect to the dashboard
      navigate('/dashboard');
    } catch (err) {
      // Set the error message
      setError(err.message);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-main-color">
      <div className="w-full max-w-md p-8 bg-white shadow-md rounded-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        {error && <p className="text-error mb-3">{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="Email Or Username"
              required
            />
            <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder='Password'
              required
            />
          <button
            type="submit"
            className="w-full p-2 bg-main-color text-white rounded-md hover:bg-orange"
          >
            Login
            
          </button>
        </form>
        <div className="mt-6 flex items-center justify-between">
            <span className="block h-0.5 bg-light-purple w-full"></span>
            <span className="w-full justify-center text-gray pl-4">Or Sign In with</span>
            <span className="block h-0.5 bg-light-purple w-full"></span>
          </div>

          <div className="mt-4 flex justify-center">
            <button className="w-full bg-white text-gray py-2 rounded flex items-center justify-center hover:bg-gray-100">
              {/* Add icon for Google signup here */}
              <div className="w-12 h-12 rounded-full bg-place-holder flex items-center justify-center">
                  <img
                    src="icon _google_.svg"
                    alt="Profile"
                    className="w-6 h-6 object-cover rounded-full"
                  />
              
              </div>
            </button>
          </div>
        <p className="mt-6 text-center text-gray">
            Create an account?{" "}
            <a href="/register" className="text-main-color hover:text-orange">
              Sign Up
            </a>
          </p>
      </div>
    </div>
  );
};

export default LoginPage;
