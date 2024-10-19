import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000'; // Replace with your backend URL

// Define your login function
export const login = async (identifier, password) => {
  try {
    const response = await axios.post(`${API_URL}/auth/login`, {
      identifier,
      password,
    });

    // Return the response if successful
    return response.data;
  } catch (error) {
    // Handle errors
    throw new Error('Incorrect Email/Username or Password');
  }
};


// Function to register a new user
export const registerUser = async (userData) => {
  const formData = new FormData();

  // Append the form fields to the FormData object
  formData.append('firstname', userData.firstname);
  formData.append('lastname', userData.lastname);
  formData.append('username', userData.username);
  formData.append('email', userData.email);
  formData.append('password', userData.password);

  // If a profile picture was uploaded, append it to the formData
  if (userData.profile_picture) {
    formData.append('profile_picture', userData.profile_picture);
  }

  try {
    const response = await axios.post(`${API_URL}/auth/register`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;  // Success response
  } catch (error) {
    console.error('Error during registration:', error.response?.data || error.message);
    throw error;
  }
};


// Function to call logout endpoint
export const logoutUser = async (token) => {
  try {
    const response = await axios.post(`${API_URL}/auth/logout`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`, // Make sure to include 'Bearer ' before the token
      },
    });
    return response.data; // Response from the logout endpoint
  } catch (error) {
    console.error("Error logging out:", error.response?.data || error.message);
    throw error;
  }
};
