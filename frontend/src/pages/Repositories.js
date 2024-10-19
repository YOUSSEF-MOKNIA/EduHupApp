// Chat page

import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import { useNavigate } from 'react-router-dom';

const Repositories = () => {

    return (
        <div className="flex h-screen overflow-hidden">
            <Sidebar /> {/* Sidebar on the left */}
            <div className="flex-grow p-8 ml-32">
                <div className="bg-purple-50 h-screen">
                    <TopBar /> {/* Top bar for date and profile */}   
                    <div className="flex">
                        <h1 className="text-3xl font-medium">Repositories</h1>
                    </div>
                </div>
            </div>
        </div>           
    );
};
export default Repositories;