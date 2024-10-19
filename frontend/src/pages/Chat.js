// Chat page

import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import TopBar from "../components/TopBar";
import { useNavigate } from "react-router-dom";

const Chat = () => {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar /> {/* Sidebar on the left */}
      <div className="flex-grow p-8 ml-32">
        <TopBar /> {/* Top bar for date and profile */}
        <div className="flex">
          <h1 className="text-3xl font-medium">Group Chats</h1>
          <div class="h-screen">
            <div class="bg-white h-5/6 max-w-6xl shadow-lg rounded-lg p-8 mt-14">
              {/* <!-- Content goes here --> */}
              <h1 class="text-3xl font-bold">Full Screen Height White Card</h1>
              <p class="text-gray-600">
                This card takes up the full height of the screen.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
