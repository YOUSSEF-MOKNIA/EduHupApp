import React from "react";
import { Link, useLocation } from "react-router-dom"; // Assuming you are using React Router
import { LogoIcon, DashboardIcon, ChatIcon, RepoIcon, CalendarIcon, AboutIcon } from "./Icons";
import {useState} from "react";

const Sidebar = () => {
  const location = useLocation(); // Get the current route path
  const [activeItem, setActiveItem] = useState(location.pathname); // Track the active item
  const [hoveredItem, setHoveredItem] = useState(null); // Track the hovered item


  const handleItemClick = (item) => {
    setActiveItem(item); // Update the active item when clicked
  };


  const handleMouseEnter = (item) => {
    setHoveredItem(item); // Update the hovered item when mouse enters
  };

  const handleMouseLeave = () => {
    setHoveredItem(null); // Reset the hovered item when mouse leaves
  };

  // Common style classes
  const linkClasses = "flex flex-col items-center space-y-1";

  return (
    <div className="fixed h-screen w-28 bg-white flex flex-col items-center py-8 shadow-md ">
      {/* Logo or top icon */}
      <div className="mb-8">
       <LogoIcon />
      </div>

      {/* Navigation Links */}
      <nav className="flex flex-col items-center space-y-6">
      <Link
          to="/dashboard"
          className={`${linkClasses} ${activeItem === "/dashboard" ? "text-[#7A58C1]" : "text-[#4D4D4D]"} hover:text-orange`}
          onClick={() => handleItemClick("/dashboard")}
          onMouseEnter={() => handleMouseEnter("/dashboard")}
          onMouseLeave={handleMouseLeave}
        >
          <DashboardIcon
            color={
              hoveredItem === "/dashboard" ? "#FF8000" : activeItem === "/dashboard" ? "#7A58C1" : "#4D4D4D"
            }
          />
          <span className="font-medium">Dashboard</span>
        </Link>

        <Link
          to="/chat"
          className={`${linkClasses} ${activeItem === "/chat" ? "text-[#7A58C1]" : "text-[#4D4D4D]"} hover:text-orange`}
          onClick={() => handleItemClick("/chat")}
          onMouseEnter={() => handleMouseEnter("/chat")}
          onMouseLeave={handleMouseLeave}
        >
          <ChatIcon
            color={
              hoveredItem === "/chat" ? "#FF8000" : activeItem === "/chat" ? "#7A58C1" : "#4D4D4D"
            }
          />
          <span className="font-medium">Chat</span>
        </Link>

        <Link
          to="/repositories"
          className={`${linkClasses} ${activeItem === "/repositories" ? "text-[#7A58C1]" : "text-[#4D4D4D]"} hover:text-orange`}
          onClick={() => handleItemClick("/repositories")}
          onMouseEnter={() => handleMouseEnter("/repositories")}
          onMouseLeave={handleMouseLeave}
        >
          <RepoIcon
            color={
              hoveredItem === "/repositories" ? "#FF8000" : activeItem === "/repositories" ? "#7A58C1" : "#4D4D4D"
            }
          />
          <span className="font-medium">Repositories</span>
        </Link>

        <Link
          to="/calendar"
          className={`${linkClasses} ${activeItem === "/calendar" ? "text-[#7A58C1]" : "text-[#4D4D4D]"} hover:text-orange`}
          onClick={() => handleItemClick("/calendar")}
          onMouseEnter={() => handleMouseEnter("/calendar")}
          onMouseLeave={handleMouseLeave}
        >
          <CalendarIcon
            color={
              hoveredItem === "/calendar" ? "#FF8000" : activeItem === "/calendar" ? "#7A58C1" : "#4D4D4D"
            }
          />
          <span className="font-medium">Calendar</span>
        </Link>

        <Link
          to="/about"
          className={`${linkClasses} ${activeItem === "/about" ? "text-[#7A58C1]" : "text-[#4D4D4D]"} hover:text-orange`}
          onClick={() => handleItemClick("/about")}
          onMouseEnter={() => handleMouseEnter("/about")}
          onMouseLeave={handleMouseLeave}
        >
          <AboutIcon
            color={
              hoveredItem === "/about" ? "#FF8000" : activeItem === "/about" ? "#7A58C1" : "#4D4D4D"
            }
          />
          <span className="font-medium">About us</span>
        </Link>
      </nav>
    </div>
  );
};

export default Sidebar;
