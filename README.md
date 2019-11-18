# [Lance's Blog](http://www.simple-code.cn)



### Abstract

This is lance's blog,  a full stack developer, this blog implemented by Python,
welcome to sign up to my site and share your story.

- support article and picture
- support interactive



### Structure

![](doc\blog.png)

### APIs

##### 1. user-centre

-  __create a user:__     /user-centre/user     POST

  - request:

  | params     | value            | type | comment |
  | ---------- | ---------------- | ---- | ------- |
  | username   | lance            | str  |         |
  | email      | 739056672@qq.com | str  |         |
  | password   | ************     | str  |         |
  | email_code | 3245             | str  |         |

  - response:
    - 201(Created)
    - 400(Parameters invalid)

- __modify user info__:    /user-centre/{user_id}    PUT

  - request:

  | params   | value        | type | comment |
  | -------- | ------------ | ---- | ------- |
  | password | ************ | str  |         |

  - response:
    - 200(OK)
    - 400(Parameters invalid)

- __login:__    /user-centre/session    POST

  - request:

  | params         | value                  | type | comment |
  | -------------- | ---------------------- | ---- | ------- |
  | email/username | lance/739056672@qq.com | str  |         |
  | password       | ************           | str  |         |
  | verify_code    | 12345                  | str  |         |

  - response:

  | params | value            | type | comment |
  | ------ | ---------------- | ---- | ------- |
  | code   | 200/204          | int  |         |
  | error  | some thing wrong | str  |         |

- __forgotten password:__    /user-centre/session    POST

  - request:

  | params         | value                  | type | comment |
  | -------------- | ---------------------- | ---- | ------- |
  | email/username | lance/739056672@qq.com | str  |         |
  | password       | ************           | str  |         |
  | verify_code    | 12345                  | str  |         |

  - response:

  | params | value            | type | comment |
  | ------ | ---------------- | ---- | ------- |
  | code   | 200/204          | int  |         |
  | error  | some thing wrong | str  |         |

