import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from models import User, Lesson, Quiz, QuizQuestion, QuestionType, DifficultyLevel
from auth import AuthHandler
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def init_database():
    """Initialize database with sample data"""
    
    # Connect to MongoDB
    mongo_url = os.environ['MONGO_URL']
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ['DB_NAME']]
    
    print("Connected to database")
    
    auth_handler = AuthHandler(db)
    
    # Create admin user
    admin_data = {
        "email": "admin@golearn.com",
        "password": "admin123",
        "full_name": "Admin User",
        "role": "admin",
        "is_verified": True
    }
    
    existing_admin = await auth_handler.get_user_by_email(admin_data["email"])
    if not existing_admin:
        admin_user = await auth_handler.create_user(admin_data)
        # Mark as verified
        await db.users.update_one(
            {"id": admin_user.id},
            {"$set": {"is_verified": True}}
        )
        print(f"Created admin user: {admin_data['email']}")
        admin_id = admin_user.id
    else:
        admin_id = existing_admin.id
        print("Admin user already exists")
    
    # Create teacher user
    teacher_data = {
        "email": "teacher@golearn.com",
        "password": "teacher123",
        "full_name": "Teacher User",
        "role": "teacher",
        "is_verified": True
    }
    
    existing_teacher = await auth_handler.get_user_by_email(teacher_data["email"])
    if not existing_teacher:
        teacher_user = await auth_handler.create_user(teacher_data)
        # Mark as verified
        await db.users.update_one(
            {"id": teacher_user.id},
            {"$set": {"is_verified": True}}
        )
        print(f"Created teacher user: {teacher_data['email']}")
        teacher_id = teacher_user.id
    else:
        teacher_id = existing_teacher.id
        print("Teacher user already exists")
    
    # Create sample lessons
    sample_lessons = [
        {
            "title": "Introduction to GO",
            "description": "Learn the basics of GO programming language, its history, and why it's used by major companies.",
            "content": """
# Introduction to GO Programming

## What is GO?

Go (also called Golang) is an open-source programming language developed by Google. It was created in 2007 by Robert Griesemer, Rob Pike, and Ken Thompson.

## Why GO?

- **Simple and Clean Syntax**: GO has a minimalist design that makes code easy to read and write
- **Fast Compilation**: Programs compile quickly, making development faster
- **Built-in Concurrency**: Goroutines make concurrent programming easy
- **Static Typing**: Catches errors at compile time
- **Garbage Collection**: Automatic memory management

## Key Features

1. **Statically Typed**: Variables must be declared with specific types
2. **Compiled Language**: Source code is compiled to machine code
3. **Cross-platform**: Runs on Windows, macOS, and Linux
4. **Open Source**: Free to use and modify

## Companies Using GO

- Google
- Uber
- Netflix
- Docker
- Kubernetes

## Your First GO Program

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

This simple program demonstrates the basic structure of a GO program.
            """,
            "difficulty": DifficultyLevel.BEGINNER,
            "estimated_time": 20,
            "go_code_examples": [
                'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}'
            ],
            "key_concepts": ["Package declaration", "Import statements", "Main function", "Print statements"],
            "points_reward": 100,
            "order_index": 1,
            "is_published": True
        },
        {
            "title": "Variables and Data Types",
            "description": "Understanding how to declare variables and work with different data types in GO.",
            "content": """
# Variables and Data Types in GO

## Variable Declaration

In GO, there are several ways to declare variables:

### Method 1: var keyword
```go
var name string
var age int
var isStudent bool
```

### Method 2: var with initialization
```go
var name string = "John"
var age int = 25
var isStudent bool = true
```

### Method 3: Short declaration
```go
name := "John"
age := 25
isStudent := true
```

## Basic Data Types

### Numeric Types
- **int**: Integer numbers (32 or 64 bit)
- **int8, int16, int32, int64**: Specific size integers
- **uint**: Unsigned integers
- **float32, float64**: Floating point numbers

### Text Types
- **string**: Text data
- **rune**: Unicode character (alias for int32)
- **byte**: Alias for uint8

### Boolean Type
- **bool**: true or false

## Examples

```go
package main

import "fmt"

func main() {
    // String variable
    var message string = "Hello GO!"
    
    // Integer variables
    var count int = 42
    var price float64 = 19.99
    
    // Boolean variable
    var isReady bool = true
    
    // Short declarations
    name := "Alice"
    score := 95
    
    fmt.Println(message)
    fmt.Println("Count:", count)
    fmt.Println("Price:", price)
    fmt.Println("Ready:", isReady)
    fmt.Println("Name:", name)
    fmt.Println("Score:", score)
}
```

## Zero Values

In GO, variables declared without initial values get "zero values":
- Numbers: 0
- Strings: ""
- Booleans: false
            """,
            "difficulty": DifficultyLevel.BEGINNER,
            "estimated_time": 30,
            "go_code_examples": [
                'var name string = "John"\nvar age int = 25\nfmt.Println(name, age)',
                'name := "Alice"\nscore := 95\nfmt.Println(name, score)'
            ],
            "key_concepts": ["Variable declaration", "Data types", "Zero values", "Short declaration"],
            "points_reward": 150,
            "order_index": 2,
            "is_published": True
        },
        {
            "title": "Control Flow - If Statements",
            "description": "Learn how to use conditional statements to make decisions in your GO programs.",
            "content": """
# Control Flow: If Statements

## Basic If Statement

```go
if condition {
    // code to execute if condition is true
}
```

### Example:
```go
age := 18

if age >= 18 {
    fmt.Println("You are an adult")
}
```

## If-Else Statement

```go
if condition {
    // code if true
} else {
    // code if false
}
```

### Example:
```go
score := 85

if score >= 90 {
    fmt.Println("Grade: A")
} else {
    fmt.Println("Grade: B or lower")
}
```

## If-Else If Chain

```go
score := 85

if score >= 90 {
    fmt.Println("Grade: A")
} else if score >= 80 {
    fmt.Println("Grade: B")
} else if score >= 70 {
    fmt.Println("Grade: C")
} else {
    fmt.Println("Grade: F")
}
```

## If with Short Statement

GO allows you to run a short statement before the condition:

```go
if x := getValue(); x > 0 {
    fmt.Println("Positive number:", x)
}
```

## Comparison Operators

- `==` : Equal to
- `!=` : Not equal to
- `<`  : Less than
- `<=` : Less than or equal
- `>`  : Greater than
- `>=` : Greater than or equal

## Logical Operators

- `&&` : AND
- `||` : OR
- `!`  : NOT

### Example:
```go
age := 25
hasLicense := true

if age >= 18 && hasLicense {
    fmt.Println("Can drive")
}
```

## Complete Example

```go
package main

import "fmt"

func main() {
    temperature := 25
    
    if temperature > 30 {
        fmt.Println("It's hot!")
    } else if temperature > 20 {
        fmt.Println("Nice weather")
    } else if temperature > 10 {
        fmt.Println("A bit cool")
    } else {
        fmt.Println("It's cold!")
    }
    
    // If with initialization
    if day := "Monday"; day == "Monday" {
        fmt.Println("Start of the work week")
    }
}
```
            """,
            "difficulty": DifficultyLevel.BEGINNER,
            "estimated_time": 35,
            "go_code_examples": [
                'if age >= 18 {\n    fmt.Println("Adult")\n}',
                'if score >= 90 {\n    fmt.Println("A")\n} else {\n    fmt.Println("B or lower")\n}'
            ],
            "key_concepts": ["If statements", "Else statements", "Comparison operators", "Logical operators"],
            "points_reward": 150,
            "order_index": 3,
            "is_published": True
        },
        {
            "title": "Loops in GO",
            "description": "Master the different types of loops available in GO programming.",
            "content": """
# Loops in GO

GO has only one type of loop: the `for` loop. However, it can be used in different ways to achieve various looping behaviors.

## Basic For Loop

```go
for i := 0; i < 5; i++ {
    fmt.Println(i)
}
```

This prints numbers 0 through 4.

## For Loop Parts

1. **Initialization**: `i := 0` (runs once at the start)
2. **Condition**: `i < 5` (checked before each iteration)
3. **Post statement**: `i++` (runs after each iteration)

## While-style Loop

```go
i := 0
for i < 5 {
    fmt.Println(i)
    i++
}
```

## Infinite Loop

```go
for {
    fmt.Println("This runs forever")
    // Use 'break' to exit
    break
}
```

## Range Loop

Used to iterate over collections:

### Over a slice:
```go
numbers := []int{1, 2, 3, 4, 5}

for index, value := range numbers {
    fmt.Println(index, value)
}
```

### Over a string:
```go
text := "Hello"

for index, char := range text {
    fmt.Println(index, string(char))
}
```

## Loop Control

### Break
Exits the loop completely:

```go
for i := 0; i < 10; i++ {
    if i == 5 {
        break // Exit when i equals 5
    }
    fmt.Println(i)
}
```

### Continue
Skips to the next iteration:

```go
for i := 0; i < 10; i++ {
    if i%2 == 0 {
        continue // Skip even numbers
    }
    fmt.Println(i) // Only prints odd numbers
}
```

## Practical Examples

### Countdown:
```go
for i := 10; i >= 1; i-- {
    fmt.Println(i)
}
fmt.Println("Blast off!")
```

### Sum calculation:
```go
sum := 0
for i := 1; i <= 100; i++ {
    sum += i
}
fmt.Println("Sum:", sum)
```

### Nested loops:
```go
for i := 1; i <= 3; i++ {
    for j := 1; j <= 3; j++ {
        fmt.Printf("(%d,%d) ", i, j)
    }
    fmt.Println()
}
```

## Complete Example

```go
package main

import "fmt"

func main() {
    // Basic counting
    fmt.Println("Counting to 5:")
    for i := 1; i <= 5; i++ {
        fmt.Println(i)
    }
    
    // While-style loop
    fmt.Println("\\nWhile-style:")
    count := 0
    for count < 3 {
        fmt.Println("Count:", count)
        count++
    }
    
    // Range over slice
    fmt.Println("\\nNumbers:")
    numbers := []int{10, 20, 30}
    for i, num := range numbers {
        fmt.Printf("Index %d: %d\\n", i, num)
    }
}
```
            """,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "estimated_time": 40,
            "go_code_examples": [
                'for i := 0; i < 5; i++ {\n    fmt.Println(i)\n}',
                'numbers := []int{1, 2, 3}\nfor i, num := range numbers {\n    fmt.Println(i, num)\n}'
            ],
            "key_concepts": ["For loops", "Range loops", "Break and continue", "Nested loops"],
            "points_reward": 200,
            "order_index": 4,
            "is_published": True
        },
        {
            "title": "Functions in GO",
            "description": "Learn how to create and use functions to organize your code effectively.",
            "content": """
# Functions in GO

Functions are blocks of code that perform specific tasks. They help organize code and make it reusable.

## Function Declaration

```go
func functionName(parameters) returnType {
    // function body
    return value
}
```

## Simple Function

```go
func greet() {
    fmt.Println("Hello, World!")
}

func main() {
    greet() // Call the function
}
```

## Function with Parameters

```go
func greet(name string) {
    fmt.Println("Hello,", name)
}

func main() {
    greet("Alice")
    greet("Bob")
}
```

## Function with Return Value

```go
func add(a int, b int) int {
    return a + b
}

func main() {
    result := add(5, 3)
    fmt.Println("Result:", result)
}
```

## Multiple Parameters of Same Type

```go
func add(a, b int) int {
    return a + b
}
```

## Multiple Return Values

GO functions can return multiple values:

```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 2)
    if err != nil {
        fmt.Println("Error:", err)
    } else {
        fmt.Println("Result:", result)
    }
}
```

## Named Return Values

```go
func rectangle(length, width float64) (area, perimeter float64) {
    area = length * width
    perimeter = 2 * (length + width)
    return // returns area and perimeter
}
```

## Variadic Functions

Functions that accept variable number of arguments:

```go
func sum(numbers ...int) int {
    total := 0
    for _, num := range numbers {
        total += num
    }
    return total
}

func main() {
    fmt.Println(sum(1, 2, 3))       // 6
    fmt.Println(sum(1, 2, 3, 4, 5)) // 15
}
```

## Function as Values

Functions can be assigned to variables:

```go
func main() {
    var operation func(int, int) int
    
    operation = func(a, b int) int {
        return a + b
    }
    
    result := operation(5, 3)
    fmt.Println(result) // 8
}
```

## Anonymous Functions

```go
func main() {
    // Anonymous function
    func() {
        fmt.Println("Anonymous function called")
    }()
    
    // Anonymous function with parameters
    double := func(x int) int {
        return x * 2
    }
    
    fmt.Println(double(5)) // 10
}
```

## Practical Examples

### Temperature converter:
```go
func celsiusToFahrenheit(celsius float64) float64 {
    return celsius*9/5 + 32
}

func fahrenheitToCelsius(fahrenheit float64) float64 {
    return (fahrenheit - 32) * 5 / 9
}
```

### Validation function:
```go
func isEven(number int) bool {
    return number%2 == 0
}

func isPositive(number int) bool {
    return number > 0
}
```

## Complete Example

```go
package main

import (
    "fmt"
    "strings"
)

func formatName(first, last string) string {
    return strings.Title(first) + " " + strings.Title(last)
}

func calculateGrade(score int) (string, bool) {
    switch {
    case score >= 90:
        return "A", true
    case score >= 80:
        return "B", true
    case score >= 70:
        return "C", true
    case score >= 60:
        return "D", true
    default:
        return "F", false
    }
}

func main() {
    // Format name
    name := formatName("john", "doe")
    fmt.Println("Formatted name:", name)
    
    // Calculate grade
    grade, passed := calculateGrade(85)
    fmt.Printf("Grade: %s, Passed: %t\\n", grade, passed)
}
```
            """,
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "estimated_time": 45,
            "go_code_examples": [
                'func greet(name string) {\n    fmt.Println("Hello,", name)\n}',
                'func add(a, b int) int {\n    return a + b\n}'
            ],
            "key_concepts": ["Function declaration", "Parameters", "Return values", "Variadic functions"],
            "points_reward": 250,
            "order_index": 5,
            "is_published": True
        }
    ]
    
    # Insert lessons
    for lesson_data in sample_lessons:
        lesson_data["created_by"] = teacher_id
        
        existing_lesson = await db.lessons.find_one({"title": lesson_data["title"]})
        if not existing_lesson:
            lesson = Lesson(**lesson_data)
            await db.lessons.insert_one(lesson.dict())
            print(f"Created lesson: {lesson_data['title']}")
        else:
            print(f"Lesson already exists: {lesson_data['title']}")
    
    # Create sample quizzes
    lessons = await db.lessons.find().to_list(10)
    
    for lesson in lessons:
        quiz_title = f"Quiz: {lesson['title']}"
        existing_quiz = await db.quizzes.find_one({"title": quiz_title})
        
        if not existing_quiz:
            # Create questions based on lesson
            questions = []
            
            if "Introduction to GO" in lesson['title']:
                questions = [
                    QuizQuestion(
                        question="Who developed the GO programming language?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options=["Microsoft", "Google", "Apple", "Facebook"],
                        correct_answer="Google",
                        explanation="GO was developed by Google in 2007.",
                        points=10
                    ),
                    QuizQuestion(
                        question="GO is a compiled language.",
                        question_type=QuestionType.TRUE_FALSE,
                        correct_answer="true",
                        explanation="GO is indeed a compiled language, which means source code is compiled to machine code.",
                        points=5
                    )
                ]
            elif "Variables" in lesson['title']:
                questions = [
                    QuizQuestion(
                        question="Which of the following is the correct way to declare a variable in GO?",
                        question_type=QuestionType.MULTIPLE_CHOICE,
                        options=["var name string", "string name", "name: string", "declare name string"],
                        correct_answer="var name string",
                        explanation="The correct syntax is 'var name string'.",
                        points=10
                    ),
                    QuizQuestion(
                        question="What is the zero value of a string in GO?",
                        question_type=QuestionType.FREE_TEXT,
                        correct_answer='""',
                        explanation="The zero value of a string in GO is an empty string \"\".",
                        points=15
                    )
                ]
            else:
                # Generic questions for other lessons
                questions = [
                    QuizQuestion(
                        question=f"This quiz covers the topic: {lesson['title']}",
                        question_type=QuestionType.TRUE_FALSE,
                        correct_answer="true",
                        explanation="This is a sample question for practice.",
                        points=10
                    )
                ]
            
            quiz = Quiz(
                title=quiz_title,
                description=f"Test your knowledge of {lesson['title']}",
                lesson_id=lesson['id'],
                questions=questions,
                created_by=teacher_id,
                time_limit=15,
                passing_score=70,
                max_points=sum(q.points for q in questions)
            )
            
            await db.quizzes.insert_one(quiz.dict())
            print(f"Created quiz: {quiz_title}")
    
    print("Database initialization completed!")
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database())