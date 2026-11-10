# 🔐 SecureVault – Secure Cloud Storage System

## 1. Project Overview

SecureVault is a cryptography-based web application developed as part of our Security Fundamentals and Development group project.

The application is based on **Use Case 6: Secure Cloud Storage** from the project brief. It aims to provide users with a secure environment in which they can register, authenticate, upload, store and download files.

The system incorporates cryptographic techniques to protect sensitive information, including secure password hashing and authenticated file encryption. It also aims to ensure that users can only access their own stored files.

## 2. Project Objectives

The main objectives of SecureVault are to:

- Develop a secure web-based cloud storage application.
- Implement user registration and authentication.
- Protect stored passwords using Argon2id.
- Implement AES-256-GCM encryption and decryption for files.
- Provide secure file uploading, storage and downloading.
- Restrict file access according to user authentication and ownership.
- Demonstrate the practical application of cryptographic security principles.

## 3. Related Cybersecurity Case Study

### Snowflake Customer Data Theft (2024)

Alongside the programming project, our group is researching the 2024 Snowflake customer data theft campaign, which affected or was associated with high-profile organisations including Ticketmaster, Santander and AT&T.

The campaign involved threat actors obtaining previously exposed customer credentials, primarily through infostealer malware, and using them to access customer Snowflake environments.

Mandiant tracked the financially motivated threat activity as UNC5537. Its investigation identified several contributing security weaknesses, including accounts without multi-factor authentication (MFA), credentials that remained valid after being stolen, and insufficient network access restrictions.

The attackers accessed customer database environments, extracted sensitive information and attempted to extort affected organisations or sell stolen data.

The incident demonstrates the importance of:

- Strong authentication and multi-factor authentication.
- Secure password management and credential protection.
- Restricting access to sensitive cloud environments.
- Monitoring suspicious account activity.
- Protecting the confidentiality and integrity of stored information.

### Connection to SecureVault

The Snowflake incident demonstrates the risks associated with storing large amounts of sensitive information in cloud environments without sufficient access controls.

This project, SecureVault, addresses related security concerns through its use of cryptographic protection, secure authentication and user-specific file access controls.

This study provides a real-world example of why secure cloud storage and effective access management are important.

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Flask | Web application framework |
| SQLite | Database management |
| HTML5 and CSS3 | Website structure and styling |
| JavaScript | Client-side functionality |
| Web Crypto API | Browser-side cryptographic operations |
| Argon2id | Password hashing |
| AES-256-GCM | Authenticated file encryption |
| Git and GitHub | Version control and collaboration |

## 5. Main Application Features

- User registration and authentication.
- Secure password hashing and verification.
- Session-based login and logout.
- Protected user dashboard.
- Secure file uploading and downloading.
- File encryption and decryption.
- User-specific file access.

## 6. Security Implementation

SecureVault focuses on the cryptographic principles of confidentiality, integrity and authentication.

### Argon2id – Password Hashing

Passwords are hashed before being stored in the database. During login, the submitted password is verified against the stored hash rather than comparing or retrieving plaintext passwords.

### AES-256-GCM – File Encryption

AES-256-GCM is intended to protect stored file contents using authenticated encryption. It provides confidentiality and integrity protection through encryption and authentication tags.

### Access Control

Session-based authentication protects restricted application pages. User-specific access controls are intended to prevent users from accessing files belonging to other accounts.

## 7. Team Contributions

| Team Member | Responsibilities |
|---|---|
| Member 1 | Website development, user registration, login, dashboard and password security. |
| Member 2 | Client-side file encryption and decryption using the Web Crypto API. |
| Member 3 | Backend development, database management, file storage and access control. |

## 8. Installation and Setup

### Prerequisites
- Python 3.11 or later
- Git
- Visual Studio Code or another Python-compatible IDE

### Clone the repository

```bash
git clone https://github.com/nicoola91/CA1-Cryptography.git
cd CA1-Cryptography
```

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate the environment (Windows PowerShell)

```powershell
.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```


### Run the application

Set the Flask secret key in Windows PowerShell:

```powershell
$env:FLASK_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
```

Start the application:

```powershell
python -m flask --app app run --port 5002
```

Open the application in your browser:

http://127.0.0.1:5002
```



## 9. Testing

Testing will cover:

- Successful and unsuccessful registration.
- Duplicate email registration.
- Successful and unsuccessful login.
- Password hashing and verification.
- Unauthorised dashboard access.
- Logout and session termination.
- File encryption and decryption.
- Detection of modified encrypted files.
- Prevention of unauthorised file access.

## 10. Future Improvements

Potential improvements include:

- Multi-factor authentication.
- Password reset functionality.
- Enhanced session security.
- Additional file management features.
- Improved monitoring and security logging.

## 11. References

- Mandiant / Google Cloud, *UNC5537 Targets Snowflake Customer Instances for Data Theft and Extortion* (10 June 2024): https://cloud.google.com/blog/topics/threat-intelligence/unc5537-snowflake-data-theft-extortion
- Snowflake, *Detecting and Preventing Unauthorized User Access*: https://medium.com/snowflake/detecting-and-preventing-unauthorized-user-access-d67be8bd66f6

## 12. Contributors
- [Nicole Byrne](https://github.com/nicoola91)
- [Sarah Pettigrew]()
- [Imaan Ahmed](https://github.com/faith7867)

*Developed collaboratively as part of the Security Fundamentals and Development group project. (3rd Year - BSc (Hons) in Computing at National College of Ireland)*
