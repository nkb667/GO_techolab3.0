import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonsAPI, quizzesAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { 
  BookOpen, 
  Clock, 
  Star, 
  CheckCircle, 
  ArrowLeft, 
  ArrowRight,
  Play,
  Trophy
} from 'lucide-react';

const LessonView = () => {
  const { lessonId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [lesson, setLesson] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [isStarted, setIsStarted] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (lessonId) {
      fetchLessonData();
    }
  }, [lessonId]);

  const fetchLessonData = async () => {
    try {
      // Fetch lesson details
      const lessonResponse = await lessonsAPI.getLesson(lessonId);
      setLesson(lessonResponse.data);

      // Fetch quizzes for the lesson
      const quizzesResponse = await quizzesAPI.getLessonQuizzes(lessonId);
      setQuizzes(quizzesResponse.data);

      // For demo purposes, set some mock progress
      setProgress(Math.random() * 100);
      
    } catch (error) {
      console.error('Error fetching lesson:', error);
      setError('Failed to load lesson. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartLesson = async () => {
    try {
      await lessonsAPI.startLesson(lessonId);
      setIsStarted(true);
      setSuccess('Lesson started! Keep going to earn points.');
    } catch (error) {
      console.error('Error starting lesson:', error);
    }
  };

  const handleCompleteLesson = async () => {
    try {
      await lessonsAPI.completeLesson(lessonId);
      setIsCompleted(true);
      setProgress(100);
      setSuccess(`Congratulations! You earned ${lesson.points_reward} points!`);
    } catch (error) {
      console.error('Error completing lesson:', error);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatContent = (content) => {
    // Simple markdown-like formatting for display
    return content
      .replace(/^# (.*$)/gm, '<h1 class="text-3xl font-bold mb-4 text-gray-900">$1</h1>')
      .replace(/^## (.*$)/gm, '<h2 class="text-2xl font-semibold mb-3 text-gray-800 mt-6">$1</h2>')
      .replace(/^### (.*$)/gm, '<h3 class="text-xl font-medium mb-2 text-gray-700 mt-4">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      .replace(/```go\n([\s\S]*?)\n```/g, '<pre class="bg-gray-900 text-green-400 p-4 rounded-lg mb-4 overflow-x-auto"><code>$1</code></pre>')
      .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-100 p-4 rounded-lg mb-4 overflow-x-auto"><code class="text-gray-800">$1</code></pre>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-100 px-2 py-1 rounded text-sm font-mono">$1</code>')
      .replace(/\n\n/g, '</p><p class="mb-4">')
      .replace(/\n/g, '<br/>');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Alert variant="destructive">
          <AlertDescription>
            {error || 'Lesson not found'}
          </AlertDescription>
        </Alert>
        <Button onClick={() => navigate('/lessons')} className="mt-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Lessons
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/lessons')}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Lessons
        </Button>
        
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
          <div className="mb-4 lg:mb-0">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{lesson.title}</h1>
            <p className="text-gray-600">{lesson.description}</p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
            <Badge className={getDifficultyColor(lesson.difficulty)}>
              {lesson.difficulty}
            </Badge>
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-1" />
              {lesson.estimated_time} minutes
            </div>
            <div className="flex items-center text-sm text-yellow-600">
              <Star className="w-4 h-4 mr-1" />
              {lesson.points_reward} points
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {success && (
        <Alert className="mb-6 border-green-200 bg-green-50">
          <CheckCircle className="w-4 h-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Progress Section */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <BookOpen className="w-5 h-5 mr-2" />
              Your Progress
            </CardTitle>
            <div className="text-sm text-gray-600">
              {Math.round(progress)}% Complete
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Progress value={progress} className="mb-4" />
          <div className="flex space-x-3">
            {!isStarted && (
              <Button onClick={handleStartLesson}>
                <Play className="w-4 h-4 mr-2" />
                Start Lesson
              </Button>
            )}
            
            {isStarted && !isCompleted && (
              <Button onClick={handleCompleteLesson}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Complete Lesson
              </Button>
            )}
            
            {isCompleted && (
              <Button disabled className="bg-green-600">
                <Trophy className="w-4 h-4 mr-2" />
                Completed!
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Key Concepts */}
      {lesson.key_concepts && lesson.key_concepts.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Key Concepts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {lesson.key_concepts.map((concept, index) => (
                <Badge key={index} variant="outline">
                  {concept}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Lesson Content */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Lesson Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div 
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ 
              __html: `<p class="mb-4">${formatContent(lesson.content)}</p>` 
            }}
          />
        </CardContent>
      </Card>

      {/* Code Examples */}
      {lesson.go_code_examples && lesson.go_code_examples.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Code Examples</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {lesson.go_code_examples.map((code, index) => (
                <div key={index}>
                  <h4 className="font-medium mb-2">Example {index + 1}:</h4>
                  <pre className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto">
                    <code>{code}</code>
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quizzes */}
      {quizzes.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Practice Quiz</CardTitle>
            <CardDescription>
              Test your understanding with these quizzes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {quizzes.map((quiz) => (
                <div key={quiz.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <h4 className="font-medium">{quiz.title}</h4>
                    <p className="text-sm text-gray-600">
                      {quiz.questions?.length || 0} questions • {quiz.time_limit || 15} minutes
                    </p>
                  </div>
                  <Button size="sm">
                    Take Quiz
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex justify-between items-center">
        <Button variant="outline" onClick={() => navigate('/lessons')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          All Lessons
        </Button>
        
        <Button onClick={() => navigate('/lessons')}>
          Next Lesson
          <ArrowRight className="w-4 h-4 ml-2" />
        </Button>
      </div>
    </div>
  );
};

export default LessonView;