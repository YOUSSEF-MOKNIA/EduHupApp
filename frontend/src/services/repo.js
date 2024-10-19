// services/repoService.js
import axios from 'axios';


const API_URL = 'http://127.0.0.1:8000'; // Replace with your backend URL

// Function to fetch pinned repositories
export const getPinnedRepos = async () => {
  try {
    const response = await axios.get(`${API_URL}/repo/pinned`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,  // Assuming you're using JWT for authentication
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching pinned repositories:", error);
    throw error;
  }
};

// Function to get the number of documents in a repository
export const getRepoDocumentCount = async (repoId) => {
    try {
      const response = await axios.get(`${API_URL}/repo/${repoId}/count`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      return response.data.count; // Assuming your backend returns the count as 'count'
    } catch (error) {
      console.error("Error fetching document count:", error);
      throw error;
    }
  };

// Function to fetch recently added files across all repositories the user is a member of
export const getRecentFilesAcrossRepos = async () => {
  try {
    const response = await axios.get(`${API_URL}/repo/recent-files`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,  // Assuming you're using JWT for authentication
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching recent files:", error);
    throw error;
  }
};

// Unpinn a repository
export const unpinRepo = async (repoId) => {
  try {
    const response = await axios.put(`${API_URL}/repo/unpin/${repoId}`, {}, {
      headers: { 
        Authorization: `Bearer ${localStorage.getItem('token')}`,  // Assuming you're using JWT for authentication
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error unpinning repository:", error);
    throw error;
  }
};
