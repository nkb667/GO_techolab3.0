import React, { useState, useEffect } from 'react';
import { lessonsAPI } from '../services/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { BookOpen, Clock, Star, Search, Filter } from 'lucide-react';
import { Link } from 'react-router-dom';

const Lessons = () => {
  const [lessons, setLessons] = useState([]);
  const [filteredLessons, setFilteredLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('all');

  useEffect(() => {
    fetchLessons();
  }, []);

  useEffect(() => {
    filterLessons();
  }, [lessons, searchTerm, difficultyFilter]);

  const fetchLessons = async () => {
    try {
      const response = await lessonsAPI.getLessons();
      setLessons(response.data);
    } catch (error) {
      console.error('Error fetching lessons:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterLessons = () => {
    let filtered = lessons;

    // Search filter
    if (searchTerm.trim()) {
      const search = searchTerm.toLowerCase().trim();
      filtered = filtered.filter(lesson =>
        lesson.title.toLowerCase().includes(search) ||
        lesson.description?.toLowerCase().includes(search) ||
        (lesson.key_concepts && lesson.key_concepts.some(concept => 
          concept.toLowerCase().includes(search)
        ))
      );
    }

    // Difficulty filter
    if (difficultyFilter !== 'all') {
      filtered = filtered.filter(lesson => lesson.difficulty === difficultyFilter);
    }

    setFilteredLessons(filtered);
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyIcon = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return '🟢';
      case 'intermediate': return '🟡';
      case 'advanced': return '🔴';
      default: return '⚪';
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
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">GO Programming Lessons</h1>
        <p className="text-gray-600 mt-2">Master the fundamentals of GO programming step by step</p>
      </div>

      {/* Filters */}
      <div className="mb-8">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search lessons..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          <div className="sm:w-48">
            <Select value={difficultyFilter} onValueChange={setDifficultyFilter}>
              <SelectTrigger>
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* Lessons Grid */}
      {filteredLessons.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No lessons found</h3>
          <p className="text-gray-600">
            {searchTerm || difficultyFilter !== 'all' 
              ? 'Try adjusting your search or filter criteria'
              : 'No lessons are available yet. Check back soon!'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredLessons.map((lesson) => (
            <Card key={lesson.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2">{lesson.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {lesson.description || 'Learn the fundamentals of GO programming.'}
                    </CardDescription>
                  </div>
                  <div className="text-2xl ml-4">
                    {getDifficultyIcon(lesson.difficulty)}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                <div className="space-y-4">
                  {/* Lesson Info */}
                  <div className="flex items-center justify-between text-sm text-gray-600">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {lesson.estimated_time} min
                    </div>
                    <div className="flex items-center">
                      <Star className="h-4 w-4 mr-1 text-yellow-500" />
                      {lesson.points_reward} points
                    </div>
                  </div>

                  {/* Difficulty Badge */}
                  <div className="flex items-center justify-between">
                    <Badge 
                      variant="secondary" 
                      className={getDifficultyColor(lesson.difficulty)}
                    >
                      {lesson.difficulty}
                    </Badge>
                    
                    {/* Key Concepts Preview */}
                    {lesson.key_concepts && lesson.key_concepts.length > 0 && (
                      <div className="text-xs text-gray-500">
                        {lesson.key_concepts.slice(0, 2).join(', ')}
                        {lesson.key_concepts.length > 2 && '...'}
                      </div>
                    )}
                  </div>

                  {/* Action Button */}
                  <Link to={`/lessons/${lesson.id}`} className="block">
                    <Button className="w-full">
                      Start Lesson
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Learning Path Info */}
      {filteredLessons.length > 0 && (
        <div className="mt-12 bg-blue-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">📚 Your Learning Path</h3>
          <p className="text-blue-800 mb-4">
            Follow our structured curriculum designed to take you from beginner to advanced GO programmer.
          </p>
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline" className="bg-white">Variables & Types</Badge>
            <Badge variant="outline" className="bg-white">Control Flow</Badge>
            <Badge variant="outline" className="bg-white">Functions</Badge>
            <Badge variant="outline" className="bg-white">Structs & Interfaces</Badge>
            <Badge variant="outline" className="bg-white">Concurrency</Badge>
            <Badge variant="outline" className="bg-white">Web Development</Badge>
          </div>
        </div>
      )}
    </div>
  );
};

export default Lessons;