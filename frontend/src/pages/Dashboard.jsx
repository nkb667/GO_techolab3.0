import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { lessonsAPI, usersAPI } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { 
  BookOpen, 
  Trophy, 
  Target, 
  Clock, 
  TrendingUp, 
  Star,
  Users,
  GraduationCap,
  Award
} from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const { user } = useAuth();
  const [lessons, setLessons] = useState([]);
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    completedLessons: 0,
    totalLessons: 0,
    points: 0,
    streak: 0,
    rank: 0
  });

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch lessons
      const lessonsResponse = await lessonsAPI.getLessons();
      setLessons(lessonsResponse.data.slice(0, 6)); // Show first 6 lessons

      // Fetch user achievements
      if (user?.id) {
        try {
          const achievementsResponse = await usersAPI.getUserAchievements(user.id);
          setAchievements(achievementsResponse.data.slice(0, 3)); // Show first 3 achievements
        } catch (error) {
          console.log('Achievements not available yet');
        }
      }

      // Mock stats for now (would come from API in real app)
      setStats({
        completedLessons: 12,
        totalLessons: lessonsResponse.data.length,
        points: user?.points || 0,
        streak: user?.streak_days || 0,
        rank: 15
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const progressPercentage = stats.totalLessons > 0 
    ? Math.round((stats.completedLessons / stats.totalLessons) * 100) 
    : 0;

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    const timeOfDay = hour < 12 ? 'morning' : hour < 18 ? 'afternoon' : 'evening';
    return `Good ${timeOfDay}, ${user?.full_name?.split(' ')[0] || 'there'}!`;
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">{getWelcomeMessage()}</h1>
        <p className="text-gray-600 mt-2">Ready to continue your GO programming journey?</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <BookOpen className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Progress</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.completedLessons}/{stats.totalLessons}
                </p>
              </div>
            </div>
            <Progress value={progressPercentage} className="mt-4" />
            <p className="text-xs text-gray-500 mt-2">{progressPercentage}% completed</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Trophy className="h-8 w-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Points</p>
                <p className="text-2xl font-bold text-gray-900">{stats.points}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Target className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Streak</p>
                <p className="text-2xl font-bold text-gray-900">{stats.streak} days</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Rank</p>
                <p className="text-2xl font-bold text-gray-900">#{stats.rank}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Lessons */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Continue Learning</CardTitle>
                  <CardDescription>Pick up where you left off</CardDescription>
                </div>
                <Link to="/lessons">
                  <Button variant="outline">View All</Button>
                </Link>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {lessons.map((lesson) => (
                  <div 
                    key={lesson.id} 
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-100 p-2 rounded-lg">
                        <GraduationCap className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{lesson.title}</h3>
                        <p className="text-sm text-gray-600">
                          {lesson.estimated_time} minutes
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Badge 
                        variant="secondary" 
                        className={getDifficultyColor(lesson.difficulty)}
                      >
                        {lesson.difficulty}
                      </Badge>
                      <Link to={`/lessons/${lesson.id}`}>
                        <Button size="sm">Continue</Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Achievements & Quick Actions */}
        <div className="space-y-6">
          {/* Recent Achievements */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Award className="h-5 w-5 mr-2 text-yellow-500" />
                Recent Achievements
              </CardTitle>
            </CardHeader>
            <CardContent>
              {achievements.length > 0 ? (
                <div className="space-y-3">
                  {achievements.map((achievement, index) => (
                    <div key={index} className="flex items-center space-x-3 p-3 bg-yellow-50 rounded-lg">
                      <div className="text-2xl">🏆</div>
                      <div>
                        <p className="font-medium text-gray-900">Achievement Earned!</p>
                        <p className="text-sm text-gray-600">Great progress!</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Award className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No achievements yet</p>
                  <p className="text-sm text-gray-400 mt-2">Complete lessons to earn your first achievement!</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {user?.role === 'student' && (
                <>
                  <Link to="/lessons" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <BookOpen className="h-4 w-4 mr-2" />
                      Browse Lessons
                    </Button>
                  </Link>
                  <Link to="/achievements" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <Trophy className="h-4 w-4 mr-2" />
                      View Achievements
                    </Button>
                  </Link>
                </>
              )}

              {user?.role === 'teacher' && (
                <>
                  <Link to="/classes" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <Users className="h-4 w-4 mr-2" />
                      Manage Classes
                    </Button>
                  </Link>
                  <Link to="/lessons/create" className="block">
                    <Button variant="outline" className="w-full justify-start">
                      <BookOpen className="h-4 w-4 mr-2" />
                      Create Lesson
                    </Button>
                  </Link>
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;