import React, { useState } from "react";
import { registerUser } from "../services/Auth"; // Import the service
import { useNavigate } from 'react-router-dom'; // Import useNavigate from React Router


const Register = () => {
  const [formData, setFormData] = useState({
    firstname: "",
    lastname: "",
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    profile_picture: null,
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [imagePreview, setImagePreview] = useState(null); // To preview selected image
  const navigate = useNavigate(); // Initialize useNavigate for redirection


  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  // Handle profile picture upload
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData((prevData) => ({
      ...prevData,
      profile_picture: file,
    }));
    // Create a preview of the selected image
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    if (file) {
      reader.readAsDataURL(file);
    }
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }
    try {
      const response = await registerUser(formData);
      setSuccess(response.message);
      setError("");
      // Redirect to the dashboard after successful login
      navigate('/login');
    } catch (error) {
      setError("Registration failed. Please try again.");
      setSuccess("");
    }
  };

  return (
    <div className="flex min-h-screen bg-main-color items-center justify-center">
      {/* Left side - Logo and Illustration */}
      <div className="w-1/2 flex flex-col  p-10 text-white">
        <h1 className="text-5xl font-bold mb-6">EduHub</h1>
        <p className="text-2xl mb-8">
          Unlock knowledge, connect, and collaborate effortlessly.
        </p>
        {/* You can replace this with an image */}
        {/* <img src="No connection.svg" alt="Illustration" className="w-4/6" /> */}
      </div>

      {/* Right side - White Card with Form */}
      <div className="w-1/2 flex items-center justify-center">
        <div className="bg-white p-10 rounded-lg shadow-lg w-full max-w-lg">
          <h2 className="text-3xl font-semibold mb-6 text-center">
            Create Account
          </h2>

          <form onSubmit={handleSubmit} encType="multipart/form-data">
          <div className="flex justify-center items-center mb-6">
            <label htmlFor="profilePicture" className="cursor-pointer">
              {/* Circle container for profile picture upload */}
              <div className="w-24 h-24 rounded-full bg-place-holder flex items-center justify-center">
                {imagePreview ? (
                  <img
                    src={imagePreview}
                    alt="Profile"
                    className="w-full h-full object-cover rounded-full"
                  />
                ) : (
                  // Default user icon if no picture is uploaded
                  <img
                    src="iconamoon_profile-fill.svg" // Adjust to the actual path of your SVG
                    alt="User Icon"
                    className="w-12 h-12"
                  />
                )}
              </div>
            </label>
            <input
              type="file"
              id="profilePicture"
              name="profile_picture"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
            />
          </div>

          {error && <p className="text-error mb-4">{error}</p>}
          {success && <p className="text-success mb-4">{success}</p>}

            <div className="flex gap-4">
              <input
                className="w-1/2 bg-place-holder px-3 py-2 mb-4 rounded-full"
                type="text"
                name="firstname"
                placeholder="Firstname"
                value={formData.firstname}
                onChange={handleChange}
                required
              />
              <input
                className="w-1/2 bg-place-holder px-3 py-2 mb-4 rounded-full"
                type="text"
                name="lastname"
                placeholder="Lastname"
                value={formData.lastname}
                onChange={handleChange}
                required
              />
            </div>
            <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="text"
              name="username"
              placeholder="Username"
              value={formData.username}
              onChange={handleChange}
              required
            />
            <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="email"
              name="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={handleChange}
              required
            />
            <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
            />
            <input
              className="w-full bg-place-holder px-3 py-2 mb-4 rounded-full"
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />

            <button
              className="w-full bg-main-color text-white px-3 py-2 rounded-full hover:bg-purple-700"
              type="submit"
            >
              Sign Up
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between">
            <span className="block h-0.5 bg-light-purple w-full"></span>
            <span className="w-full justify-center pl-4 text-gray">Or Sign Up with</span>
            <span className="block h-0.5 bg-light-purple w-full"></span>
          </div>

          <div className="mt-4 flex justify-center">
            <button className="w-full bg-white text-gray-500 py-2 rounded flex items-center justify-center hover:bg-gray-100">
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

          <p className="mt-6 text-center text-gray-500">
            Already have an account?{" "}
            <a href="/" className="text-main-color hover:text-orange">
              Sign In
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
