import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button } from '../ui/button';
import { Avatar } from '../ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { User, LogOut, Settings, BookOpen, Award } from 'lucide-react';

const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'text-red-500';
      case 'teacher': return 'text-blue-500';
      case 'student': return 'text-green-500';
      default: return 'text-gray-500';
    }
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center space-x-2">
              <div className="bg-blue-600 text-white p-2 rounded-lg">
                <BookOpen className="w-6 h-6" />
              </div>
              <span className="text-xl font-bold text-gray-900">GO Learn</span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-4">
              <Link 
                to="/dashboard" 
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Dashboard
              </Link>
              
              {user?.role === 'student' && (
                <>
                  <Link 
                    to="/lessons" 
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Lessons
                  </Link>
                  <Link 
                    to="/achievements" 
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    <Award className="w-4 h-4 inline mr-1" />
                    Achievements
                  </Link>
                </>
              )}

              {user?.role === 'teacher' && (
                <>
                  <Link 
                    to="/classes" 
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Classes
                  </Link>
                  <Link 
                    to="/lessons" 
                    className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                  >
                    Lessons
                  </Link>
                </>
              )}

              {user?.role === 'admin' && (
                <Link 
                  to="/admin" 
                  className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Admin
                </Link>
              )}
            </div>
          </div>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {/* Points Display */}
            <div className="hidden sm:flex items-center space-x-2 bg-yellow-100 px-3 py-1 rounded-full">
              <Award className="w-4 h-4 text-yellow-600" />
              <span className="text-sm font-medium text-yellow-800">{user?.points || 0} points</span>
            </div>

            {/* User Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-10 w-10 rounded-full">
                  <Avatar className="h-10 w-10">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-600 h-full w-full flex items-center justify-center text-white font-semibold">
                      {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">{user?.full_name}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                    <p className={`text-xs font-medium ${getRoleColor(user?.role)} capitalize`}>
                      {user?.role}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="cursor-pointer">
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer">
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="cursor-pointer" onClick={handleLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;