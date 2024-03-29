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

# Create tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        UserID INT PRIMARY KEY AUTO_INCREMENT,
        Username VARCHAR(255),
        Password VARCHAR(255),
        FullName VARCHAR(255),
        Email VARCHAR(255),
        Role VARCHAR(255)
    );
    CREATE TABLE IF NOT EXISTS projects (
        ProjectID INT PRIMARY KEY AUTO_INCREMENT,
        ProjectName VARCHAR(255),
        Description TEXT,
        StartDate DATE,
        EndDate DATE,
        Status BOOLEAN,
        ModifiedTimestamp TIMESTAMP NOT NULL,
        CreatedByUserID INT NOT NULL,
        LastModifiedByUserID INT,
        FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID),
        FOREIGN KEY (CreatedByUserID) REFERENCES users(UserID)

    );
    CREATE TABLE IF NOT EXISTS collaborators (
        CollaboratorID INT PRIMARY KEY AUTO_INCREMENT,
        JoinDate DATE,
        ProjectID INT,
        UserID INT,
        FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
        FOREIGN KEY (UserID) REFERENCES users(UserID)
    );
    CREATE TABLE IF NOT EXISTS tasks (
        TaskID INT PRIMARY KEY AUTO_INCREMENT,
        TaskName VARCHAR(255),
        Description TEXT,
        Deadline DATE,
        Status BOOLEAN,
        Priority VARCHAR(10),
        ProjectID INT,
        AssigneeID INT,
        Category VARCHAR(50),
        ModifiedTimestamp TIMESTAMP NOT NULL,
        LastModifiedByUserID INT NOT NULL,
        FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
        FOREIGN KEY (AssigneeID) REFERENCES users(UserID),
        FOREIGN KEY (LastModifiedByUserID) REFERENCES users(UserID)
    );
    CREATE TABLE IF NOT EXISTS comments (
        CommentID INT PRIMARY KEY AUTO_INCREMENT,
        ProjectID INT,
        UserID INT,
        CommentText TEXT,
        ModifiedTimestamp TIMESTAMP NOT NULL,
        FOREIGN KEY (ProjectID) REFERENCES projects(ProjectID) ON DELETE CASCADE,
        FOREIGN KEY (UserID) REFERENCES users(UserID)
    );
    CREATE TABLE IF NOT EXISTS logs (   
        LogID INT PRIMARY KEY AUTO_INCREMENT,
        RecordID INT,
        ModifiedTimestamp TIMESTAMP NOT NULL,
        UserID INT NOT NULL,
        FOREIGN KEY (RecordID) REFERENCES tasks(TaskID) ON DELETE CASCADE
    );
                         
    # Add the stored procedure
    CREATE PROCEDURE GetTasksForUser (IN user_id INT)
    BEGIN
        SELECT * 
        FROM tasks
        WHERE AssigneeID = user_id;
               
        IF (ROW_COUNT() = 0) THEN
            SELECT CONCAT('No tasks found for user: ', user_id);
        END IF;
    END;
               
    CREATE TRIGGER trg_InsertCollaboratorOnProjectInsert
    AFTER INSERT
    ON projects
    FOR EACH ROW
    BEGIN
        INSERT INTO Collaborators (JoinDate, ProjectID, UserID)
        VALUES (NOW(), NEW.ProjectID, NEW.CreatedByUserID);
    END;
    

    CREATE TRIGGER trg_tasks_insert_logs
    AFTER INSERT 
    ON tasks 
    FOR EACH ROW
    BEGIN
        INSERT INTO logs (RecordID, UserID, ModifiedTimestamp)
        VALUES (NEW.TaskID, NEW.LastModifiedByUserID, NOW());  
    END;

    CREATE TRIGGER trg_tasks_update_logs
    AFTER UPDATE 
    ON tasks 
    FOR EACH ROW
    BEGIN
        INSERT INTO logs (RecordID, UserID, ModifiedTimestamp)
        VALUES (NEW.TaskID, NEW.LastModifiedByUserID, NOW());  
    END;
    
    CREATE PROCEDURE GetUserTasks(IN user_id INT)
    BEGIN
    SELECT DISTINCT
        t.*,
        p.ProjectName,  
        u.Username,
        u.Email
    FROM
        tasks t
        INNER JOIN projects p  
        ON t.ProjectID = p.ProjectID
        INNER JOIN users u
        ON t.AssigneeID = u.UserID
        INNER JOIN Collaborators c
        ON p.ProjectID = c.ProjectID
    WHERE
        t.AssigneeID = user_id OR  
        c.UserID = user_id; 
    END;

''')
'''
    # Add the trigger
    CREATE TRIGGER update_modified_timestamp
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    BEGIN
        SET NEW.ModifiedTimestamp = CURRENT_TIMESTAMP;
    END;
'''

'''
CREATE PROCEDURE GetUserTasks(IN user_id INT)
BEGIN
  SELECT DISTINCT
    t.*,
    p.ProjectName,  
    u.Username,
    u.Email
  FROM
    tasks t
    INNER JOIN projects p  
      ON t.ProjectID = p.ProjectID
    INNER JOIN users u
      ON t.AssigneeID = u.UserID
    INNER JOIN Collaborators c
      ON p.ProjectID = c.ProjectID
  WHERE
    t.AssigneeID = user_id OR  
    c.UserID = user_id; 
END
'''