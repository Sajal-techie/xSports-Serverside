Xsports Backend

Project Overview
Xsports is an innovative platform designed to connect athletes with sports academies. It serves as a dedicated space for players to showcase their skills, find opportunities, and participate in selection trials, while academies can discover talent and organize trials. The platform aims to bridge the gap between athletes and opportunities, helping them achieve their dream careers in sports.

Why Xsports?
The sports industry is highly competitive, and many talented athletes struggle to find the right opportunities to showcase their abilities. Xsports was developed to address this gap by providing a centralized platform where players can connect with academies, participate in trials, and build their sports careers. Academies, on the other hand, can efficiently manage trials and discover promising talent, making the selection process more streamlined and accessible.

Features
User Roles: Three types of users—players, academies, and admins—each with specific functionality.
Trials Management: Academies can create, manage, and monitor selection trials.
Player Registration: Players can register for trials, providing necessary details and fulfilling academy-specific requirements.
Friend and Follow System: Players can connect with each other through friend requests and follow academies to stay updated on trials and events.
Search Functionality: A robust search feature allows users to find players, academies, posts, and trials with filters and suggestions.
Posts and Interaction: Users can post, like, comment, and share content, similar to social media platforms.
Real-Time Chat: Players and academies can engage in real-time communication through the chat feature.
Admin Dashboard: Admins can oversee the platform’s activities, managing users, trials, and posts.
Installation and Setup
Prerequisites
Docker
Docker Compose
Git
AWS account for deployment (optional)
Cloning the Repository
bash
Copy code
git clone https://github.com/yourusername/xsports-platform.git
cd xsports-platform
Environment Variables
Create a .env file in the root directory and add the necessary environment variables:

env
Copy code
# Django settings
DJANGO_SECRET_KEY=your_secret_key
DATABASE_URL=postgres://username:password@hostname/dbname
DEBUG=True

# AWS credentials (for deployment)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_access_key
Building and Running with Docker
Build and run the application using Docker Compose:

bash
Copy code
docker-compose up --build
Accessing the Application
The application will be accessible at http://localhost:8000/.
Running Tests
To run tests, use the following command:

bash
Copy code
docker-compose exec web python manage.py test
Deployment
This project can be deployed using AWS EC2. You can automate the deployment process with a GitHub Actions CI/CD pipeline that builds the Docker image, pushes it to Docker Hub, and deploys it to the EC2 instance.

GitHub Actions
Here’s a brief overview of the deployment process:

Push to the master branch triggers the build and push of the Docker image to Docker Hub.
The image is then pulled and deployed to an AWS EC2 instance using Docker Compose.
Ensure your secrets (Docker Hub credentials, AWS credentials, EC2 SSH key) are securely stored in GitHub Actions secrets.

Contributing
Contributions are welcome! Please follow these steps to contribute:

Fork the repository.
Create a new branch (git checkout -b feature-branch).
Make your changes and commit them (git commit -m 'Add new feature').
Push to the branch (git push origin feature-branch).
Create a pull request.
License
This project is licensed under the MIT License. See the LICENSE file for details.

Contact
For any inquiries or feedback, please reach out to your-email@example.com.