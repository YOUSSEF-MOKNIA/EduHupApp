import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000'; // Replace with your backend URL

// Function to get the logged-in user's data
export const getCurrentUser = async () => {
  try {
    const response = await axios.get(`${API_URL}/profile/me`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,  // Assuming you're using JWT for authentication
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching user data:", error);
    throw error;
  }
};
