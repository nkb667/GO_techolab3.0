import requests
import sys
import json
from datetime import datetime

class GOLearningPlatformTester:
    def __init__(self, base_url="https://go-technolab.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return success, response_data
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Response text: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "health",
            200
        )
        return success

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_login(self, email, password):
        """Test login and get token"""
        success, response = self.run_test(
            f"Login ({email})",
            "POST",
            "auth/login",
            200,
            data={"email": email, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response.get('user', {})
            print(f"   Logged in as: {self.current_user.get('full_name', 'Unknown')} ({self.current_user.get('role', 'Unknown')})")
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_get_lessons(self):
        """Test getting all lessons"""
        success, response = self.run_test(
            "Get All Lessons",
            "GET",
            "lessons",
            200
        )
        if success:
            lessons = response if isinstance(response, list) else []
            print(f"   Found {len(lessons)} lessons")
            return lessons
        return []

    def test_get_lessons_by_difficulty(self, difficulty):
        """Test getting lessons by difficulty"""
        success, response = self.run_test(
            f"Get {difficulty.title()} Lessons",
            "GET",
            f"lessons?difficulty={difficulty}",
            200
        )
        if success:
            lessons = response if isinstance(response, list) else []
            print(f"   Found {len(lessons)} {difficulty} lessons")
            return lessons
        return []

    def test_get_lesson_by_id(self, lesson_id):
        """Test getting a specific lesson"""
        success, response = self.run_test(
            f"Get Lesson {lesson_id}",
            "GET",
            f"lessons/{lesson_id}",
            200
        )
        return success, response

    def test_start_lesson(self, lesson_id):
        """Test starting a lesson"""
        success, response = self.run_test(
            f"Start Lesson {lesson_id}",
            "POST",
            f"lessons/{lesson_id}/progress",
            200
        )
        return success

    def test_complete_lesson(self, lesson_id):
        """Test completing a lesson"""
        success, response = self.run_test(
            f"Complete Lesson {lesson_id}",
            "PUT",
            f"lessons/{lesson_id}/complete",
            200
        )
        return success

    def test_get_lesson_quizzes(self, lesson_id):
        """Test getting quizzes for a lesson"""
        success, response = self.run_test(
            f"Get Quizzes for Lesson {lesson_id}",
            "GET",
            f"lessons/{lesson_id}/quizzes",
            200
        )
        if success:
            quizzes = response if isinstance(response, list) else []
            print(f"   Found {len(quizzes)} quizzes")
            return quizzes
        return []

    def test_get_classes(self):
        """Test getting classes for current user"""
        success, response = self.run_test(
            "Get Classes",
            "GET",
            "classes",
            200
        )
        if success:
            classes = response if isinstance(response, list) else []
            print(f"   Found {len(classes)} classes")
            return classes
        return []

    def test_get_user_achievements(self, user_id):
        """Test getting user achievements"""
        success, response = self.run_test(
            f"Get User Achievements",
            "GET",
            f"users/{user_id}/achievements",
            200
        )
        if success:
            achievements = response if isinstance(response, list) else []
            print(f"   Found {len(achievements)} achievements")
            return achievements
        return []

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        old_token = self.token
        self.token = None
        
        success, response = self.run_test(
            "Unauthorized Access Test",
            "GET",
            "auth/me",
            401  # Should fail with 401
        )
        
        self.token = old_token
        return success

def main():
    print("🚀 Starting GO Learning Platform API Tests")
    print("=" * 50)
    
    tester = GOLearningPlatformTester()
    
    # Test basic endpoints first
    print("\n📋 BASIC ENDPOINT TESTS")
    print("-" * 30)
    
    if not tester.test_health_check():
        print("❌ Health check failed - API may be down")
        return 1
    
    if not tester.test_root_endpoint():
        print("❌ Root endpoint failed")
        return 1

    # Test unauthorized access
    print("\n🔒 SECURITY TESTS")
    print("-" * 30)
    
    tester.test_unauthorized_access()

    # Test authentication with different user roles
    print("\n🔐 AUTHENTICATION TESTS")
    print("-" * 30)
    
    test_users = [
        ("student@golearn.com", "student123", "Student"),
        ("teacher@golearn.com", "teacher123", "Teacher"),
        ("admin@golearn.com", "admin123", "Admin")
    ]
    
    successful_logins = []
    
    for email, password, role in test_users:
        if tester.test_login(email, password):
            successful_logins.append((email, password, role))
            
            # Test getting current user info
            tester.test_get_current_user()
            
            # Reset token for next user
            tester.token = None
    
    if not successful_logins:
        print("❌ No successful logins - cannot continue with protected endpoint tests")
        return 1

    # Continue with student user for main functionality tests
    print("\n📚 STUDENT FUNCTIONALITY TESTS")
    print("-" * 30)
    
    student_email, student_password, _ = successful_logins[0]  # Use first successful login (should be student)
    tester.test_login(student_email, student_password)
    
    # Test lessons functionality
    lessons = tester.test_get_lessons()
    
    if lessons:
        # Test getting lessons by difficulty
        for difficulty in ["beginner", "intermediate", "advanced"]:
            tester.test_get_lessons_by_difficulty(difficulty)
        
        # Test getting a specific lesson
        first_lesson = lessons[0]
        lesson_id = first_lesson.get('id')
        if lesson_id:
            success, lesson_data = tester.test_get_lesson_by_id(lesson_id)
            
            if success:
                # Test lesson progress
                tester.test_start_lesson(lesson_id)
                tester.test_complete_lesson(lesson_id)
                
                # Test getting quizzes for the lesson
                tester.test_get_lesson_quizzes(lesson_id)
    
    # Test classes functionality
    tester.test_get_classes()
    
    # Test achievements
    if tester.current_user and tester.current_user.get('id'):
        tester.test_get_user_achievements(tester.current_user['id'])

    # Test with teacher user if available
    teacher_login = next((login for login in successful_logins if login[2] == "Teacher"), None)
    if teacher_login:
        print("\n👨‍🏫 TEACHER FUNCTIONALITY TESTS")
        print("-" * 30)
        
        teacher_email, teacher_password, _ = teacher_login
        tester.test_login(teacher_email, teacher_password)
        
        # Test teacher-specific functionality
        tester.test_get_classes()
        tester.test_get_lessons()

    # Print final results
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check the output above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())