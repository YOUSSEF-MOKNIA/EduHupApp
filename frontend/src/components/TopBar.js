import React, { useEffect, useState, useRef } from 'react';
import { getCurrentUser } from '../services/user'; // Import the function
import { Link, useNavigate } from 'react-router-dom'; // Import Link for navigation
import ConfirmationModal from './ConfirmationModal'; // Import the modal component
import { logoutUser } from '../services/Auth'; // Import logoutUser service

// Function to get the formatted date
const getFormattedDate = () => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' };
  const formattedDate = new Intl.DateTimeFormat('en-US', options).format(new Date());
  return formattedDate;
};

const TopBar = () => {
  const [user, setUser] = useState(null);
  const [dropdownVisible, setDropdownVisible] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [token, setToken] = useState();
  const dropdownRef = useRef(null);
  const formattedDate = getFormattedDate();
  const navigate = useNavigate(); // For redirection

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await getCurrentUser();
        setUser(userData);
        setToken(userData.token); // Assuming userData contains the token
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    fetchUser();
  }, []);

  // Function to handle profile picture click
  const handleProfileClick = () => {
    setDropdownVisible(prevState => !prevState); // Toggle dropdown visibility
  };

  // Close dropdown if clicking outside of it
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownVisible(false); // Close dropdown
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside); // Cleanup the event listener
    };
  }, [dropdownRef]);

// Function to handle logout button click
const handleLogoutClick = () => {
  setIsModalOpen(true); // Open the modal when logout is clicked
};

   // Function to close the modal
   const handleModalClose = () => {
    setIsModalOpen(false); // Close the modal when the user cancels or confirms
  };

   // Function to handle confirmed logout
   const handleLogoutConfirm = () => {
    localStorage.removeItem('token'); // Remove the token from localStorage
    setIsModalOpen(false); // Close the modal
    navigate('/'); // Redirect to login page
  };

  return (
<div className="-mt-5 flex justify-between items-center">
      {/* Centering the date and icon */}
      <div className="flex flex-grow justify-center items-center">
        <svg width="35" height="25" viewBox="0 0 40 45" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M34.7604 5.875C36.4484 5.875 38.0673 6.54555 39.2609 7.73914C40.4544 8.93273 41.125 10.5516 41.125 12.2396V34.7604C41.125 36.4484 40.4544 38.0673 39.2609 39.2609C38.0673 40.4544 36.4484 41.125 34.7604 41.125H12.2396C10.5516 41.125 8.93273 40.4544 7.73914 39.2609C6.54555 38.0673 5.875 36.4484 5.875 34.7604V12.2396C5.875 10.5516 6.54555 8.93273 7.73914 7.73914C8.93273 6.54555 10.5516 5.875 12.2396 5.875H34.7604ZM38.1875 16.6458H8.8125V34.7604C8.8125 36.6522 10.3478 38.1875 12.2396 38.1875H34.7604C35.6693 38.1875 36.541 37.8264 37.1837 37.1837C37.8264 36.541 38.1875 35.6693 38.1875 34.7604V16.6458ZM15.1771 28.3958C15.8263 28.3958 16.4489 28.6537 16.908 29.1128C17.3671 29.5719 17.625 30.1945 17.625 30.8438C17.625 31.493 17.3671 32.1156 16.908 32.5747C16.4489 33.0338 15.8263 33.2917 15.1771 33.2917C14.5279 33.2917 13.9052 33.0338 13.4461 32.5747C12.9871 32.1156 12.7292 31.493 12.7292 30.8438C12.7292 30.1945 12.9871 29.5719 13.4461 29.1128C13.9052 28.6537 14.5279 28.3958 15.1771 28.3958ZM23.5 28.3958C24.1492 28.3958 24.7719 28.6537 25.2309 29.1128C25.69 29.5719 25.9479 30.1945 25.9479 30.8438C25.9479 31.493 25.69 32.1156 25.2309 32.5747C24.7719 33.0338 24.1492 33.2917 23.5 33.2917C22.8508 33.2917 22.2281 33.0338 21.7691 32.5747C21.31 32.1156 21.0521 31.493 21.0521 30.8438C21.0521 30.1945 21.31 29.5719 21.7691 29.1128C22.2281 28.6537 22.8508 28.3958 23.5 28.3958ZM15.1771 20.5625C15.8263 20.5625 16.4489 20.8204 16.908 21.2795C17.3671 21.7386 17.625 22.3612 17.625 23.0104C17.625 23.6596 17.3671 24.2823 16.908 24.7414C16.4489 25.2004 15.8263 25.4583 15.1771 25.4583C14.5279 25.4583 13.9052 25.2004 13.4461 24.7414C12.9871 24.2823 12.7292 23.6596 12.7292 23.0104C12.7292 22.3612 12.9871 21.7386 13.4461 21.2795C13.9052 20.8204 14.5279 20.5625 15.1771 20.5625ZM23.5 20.5625C24.1492 20.5625 24.7719 20.8204 25.2309 21.2795C25.69 21.7386 25.9479 22.3612 25.9479 23.0104C25.9479 23.6596 25.69 24.2823 25.2309 24.7414C24.7719 25.2004 24.1492 25.4583 23.5 25.4583C22.8508 25.4583 22.2281 25.2004 21.7691 24.7414C21.31 24.2823 21.0521 23.6596 21.0521 23.0104C21.0521 22.3612 21.31 21.7386 21.7691 21.2795C22.2281 20.8204 22.8508 20.5625 23.5 20.5625ZM31.8229 20.5625C32.4721 20.5625 33.0948 20.8204 33.5539 21.2795C34.0129 21.7386 34.2708 22.3612 34.2708 23.0104C34.2708 23.6596 34.0129 24.2823 33.5539 24.7414C33.0948 25.2004 32.4721 25.4583 31.8229 25.4583C31.1737 25.4583 30.5511 25.2004 30.092 24.7414C29.6329 24.2823 29.375 23.6596 29.375 23.0104C29.375 22.3612 29.6329 21.7386 30.092 21.2795C30.5511 20.8204 31.1737 20.5625 31.8229 20.5625ZM34.7604 8.8125H12.2396C11.3307 8.8125 10.459 9.17357 9.81627 9.81627C9.17357 10.459 8.8125 11.3307 8.8125 12.2396V13.7083H38.1875V12.2396C38.1875 11.3307 37.8264 10.459 37.1837 9.81627C36.541 9.17357 35.6693 8.8125 34.7604 8.8125Z" fill="#4B5563"/>
        </svg>
        <span className="ml-2 text-lg text-gray font-semibold">{formattedDate}</span>
      </div>
      <button className="mr-4">
          <svg className="w-7 h-7 text-gray-500" viewBox="0 0 50 50" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M40.3692 27.1308L36.5625 23.3241V18.2812C36.5581 14.7963 35.2618 11.4368 32.924 8.85232C30.5863 6.26782 27.3733 4.64194 23.9062 4.28906V1.40625H21.0938V4.28906C17.6267 4.64194 14.4137 6.26782 12.076 8.85232C9.73825 11.4368 8.44186 14.7963 8.4375 18.2812V23.3241L4.63078 27.1308C4.36704 27.3944 4.21883 27.7521 4.21875 28.125V32.3438C4.21875 32.7167 4.36691 33.0744 4.63063 33.3381C4.89435 33.6018 5.25204 33.75 5.625 33.75H15.4688V34.8427C15.4375 36.6268 16.0661 38.3597 17.234 39.709C18.4018 41.0582 20.0267 41.9288 21.7969 42.1538C22.7745 42.2507 23.7615 42.142 24.6946 41.8345C25.6276 41.5271 26.486 41.0278 27.2145 40.3687C27.943 39.7096 28.5255 38.9053 28.9245 38.0076C29.3235 37.1099 29.5302 36.1386 29.5312 35.1562V33.75H39.375C39.748 33.75 40.1056 33.6018 40.3694 33.3381C40.6331 33.0744 40.7812 32.7167 40.7812 32.3438V28.125C40.7812 27.7521 40.633 27.3944 40.3692 27.1308ZM26.7188 35.1562C26.7188 36.2751 26.2743 37.3482 25.4831 38.1394C24.6919 38.9305 23.6189 39.375 22.5 39.375C21.3811 39.375 20.3081 38.9305 19.5169 38.1394C18.7257 37.3482 18.2812 36.2751 18.2812 35.1562V33.75H26.7188V35.1562ZM37.9688 30.9375H7.03125V28.7072L10.838 24.9005C11.1017 24.6368 11.2499 24.2792 11.25 23.9062V18.2812C11.25 15.2976 12.4353 12.4361 14.545 10.3263C16.6548 8.21651 19.5163 7.03125 22.5 7.03125C25.4837 7.03125 28.3452 8.21651 30.455 10.3263C32.5647 12.4361 33.75 15.2976 33.75 18.2812V23.9062C33.7501 24.2792 33.8983 24.6368 34.162 24.9005L37.9688 28.7072V30.9375Z" fill="#545454"/>
          </svg>
        </button>
      {/* Profile Picture as a Link */}
      <div className="relative items-center" ref={dropdownRef}>
        {user && (
          
          <img
            src={user?.profile_picture_url || "userProfilepic.svg"} // Assuming this is the URL to the profile picture
            alt="Profile"
            className="w-12 h-12 rounded-full border-2 border-online"
            onClick={handleProfileClick} // Toggle dropdown on click
          />
        )}
       {dropdownVisible && (
            <div className="absolute right-0 mt-2  w-48 bg-white rounded shadow-xl">
              <Link to="/profile" className="block px-4 py-2 text-black hover:bg-main-color hover:text-white">
                Profile
              </Link>
              <Link to="/profile" className="block px-4 py-2 text-black hover:bg-main-color hover:text-white">
                Settings
              </Link>
              <button
                onClick={handleLogoutClick}
                className="block w-full text-left px-4 py-2 text-black hover:bg-main-color hover:text-white"
              >
                Logout
              </button>
            </div>
          )}
        <ConfirmationModal
            open={isModalOpen}
            onClose={handleModalClose}
            onConfirm={handleLogoutConfirm} // Pass the confirmed logout action
            title="Logout Confirmatiom"
            confirmationText="Are you sure you want to logout of your account!"
          /> 
       </div>
    </div>

  );
};

export default TopBar;
