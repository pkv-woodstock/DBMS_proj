import mysql.connector

db_config = {
    'host': 'localhost',
    'port': 8889,
    'user': 'root',
    'password': 'root',
}

# Create MySQL Connection
mysql_connection = mysql.connector.connect(**db_config)
cursor = mysql_connection.cursor()

cursor.execute(f'CREATE DATABASE IF NOT EXISTS taskforge')
cursor.execute(f'USE taskforge')

# Create table
cursor.execute('''
    CREATE TABLE if not exists users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(255),
    Password VARCHAR(255),
    FullName VARCHAR(255),
    Email VARCHAR(255),
    Role VARCHAR(255)
);
    CREATE TABLE if not exists projects (
    ProjectID INT PRIMARY KEY AUTO_INCREMENT,
    ProjectName VARCHAR(255),
    Description TEXT,
    StartDate DATE,
    EndDate DATE,
    Status boolean,
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists Collaborators (
    CollaboratorID INT PRIMARY KEY AUTO_INCREMENT,
    JoinDate DATE,
    ProjectID INT,
    UserID INT,
    FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists tasks (
    TaskID INT PRIMARY KEY AUTO_INCREMENT,
    TaskName VARCHAR(255),
    Description TEXT,
    Deadline DATE,
    Status BOOLEAN,
    Priority varchar(10),
    ProjectID INT,
    AssigneeID INT,
    Category VARCHAR(50),
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
    FOREIGN KEY (AssigneeID) REFERENCES users(UserID),
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists comments (
    CommentID INT PRIMARY KEY AUTO_INCREMENT,
    TaskID INT,
    UserID INT,
    CommentText TEXT,
    ModifiedTimestamp TIMESTAMP NOT NULL,
    LastModifiedByUserID INT NOT NULL,
    FOREIGN KEY (TaskID) REFERENCES tasks(TaskID) ON DELETE CASCADE,
    FOREIGN KEY (UserID) REFERENCES users(UserID),
    FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
);
    CREATE TABLE if not exists logs (
    LogID INT PRIMARY KEY AUTO_INCREMENT,
    RecordID INT,
    ModifiedTimestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (RecordID) REFERENCES tasks(TaskID) ON DELETE CASCADE
);
    ''')
mysql_connection.commit()