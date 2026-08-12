# Activity Diagrams

## 1. Login Activity

```mermaid
activityDiagram
    start
    :Navigate to /login;
    :Input Credentials;
    :Submit POST;
    if (User Exists?) then (yes)
        if (Password Matches?) then (yes)
            :Set Session Cookie;
            :Redirect to /;
            stop
        else (no)
            :Show Password Error;
        endif
    else (no)
        :Show User Not Found Error;
    endif
    stop
```

## 2. CRUD Action Activity (e.g., Delete Enrollment)

```mermaid
activityDiagram
    start
    :Click Delete Enrollment;
    :Show Confirmation Modal;
    if (Confirm?) then (yes)
        :Send DELETE API Request;
        if (Session Valid?) then (yes)
            if (Role = Admin?) then (yes)
                :Delete from Database;
                :Return 204;
                :Refresh UI Table;
            else (no)
                :Return 403 Forbidden;
                :Show Error Toast;
            endif
        else (no)
            :Return 401 Unauthorized;
            :Redirect to Login;
        endif
    else (no)
        :Close Modal;
    endif
    stop
```
