![](https://i.imgur.com/9jut70l.png)
# MHacks
![GitHub commit activity (branch)](https://img.shields.io/github/commit-activity/t/endersa1/MHacks) ![GitHub top language](https://img.shields.io/github/languages/top/endersa1/MHacks) ![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/endersa1/MHacks/pylint.yml) ![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/endersa1/MHacks) ![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/endersa1/MHacks)



## Installation
```pip install -r requirements.txt```

## Usage

### Main app
The main app is required to track user attention and alertness.
```
python main.py
```

### Data visualization
We use streamlit to visualize the data.
```
streamlit run scatter.py
```

![](https://i.imgur.com/f8rzyus.png)
![](https://i.imgur.com/xwZTFa6.png)
![](https://i.imgur.com/PFoQgM3.png)
![](https://i.imgur.com/5i8zu7z.png)


### Inspiration

The inspiration behind ALERT stems from the desire to enhance productivity and provide users with valuable insights into their computer usage habits. Recognizing the importance of maintaining focus and well-being during computer-based tasks, we aimed to create a tool that leverages various technologies to monitor eye movements, attentiveness, and overall engagement.

### What it does

ALERT is a comprehensive software solution designed to track and analyze user behavior while using a computer. It employs a combination of technologies, including eye tracking with OpenCV, monitoring heart rate through Fitbit integration, and collecting detailed information on the user's digital activities via ActivityWatch. The data collected is visualized using Streamlit, providing users with a clear overview of their computer usage patterns.

### How we built it

We built ALERT using a stack of diverse technologies:

- **Streamlit:** Utilized for data visualization, Streamlit provides an intuitive and interactive interface for users to explore and understand their computer usage data.

- **Fitbit:** Integrated Fitbit to capture and analyze heart rate data, offering insights into the user's physiological state during various computer activities.

- **ActivityWatch:** Leveraged ActivityWatch to gather detailed information about the user's interactions with different windows, tabs, and applications, enabling a holistic view of digital behavior.

- **OpenCV:** Implemented eye tracking and alertness detection using OpenCV, allowing ALERT to monitor eye movements and assess the user's level of attentiveness (looking on screen, awake).

- **Firebase:** Implemented Firebase for authentication, ensuring a secure and personalized experience for each user.

- **UMGPT:** Incorporated UMGPT (GPT-4) for natural language processing and feedback, enabling the system to provide personalized insights and suggestions based on the user's data.

### Challenges we ran into

- **Integration Complexity:** Integrating multiple technologies and ensuring seamless communication between them posed a challenge. Each component, such as eye tracking, Fitbit, and ActivityWatch, required careful integration to provide a unified user experience.

- **Data Security:** Ensuring the security and privacy of user data, especially with the integration of Fitbit and Firebase, presented challenges that required additional commitment to security.

- **Real-time Processing:** Implementing real-time processing of eye movements and attentiveness detection through OpenCV required optimization to maintain system responsiveness without compromising accuracy.

### Accomplishments that we're proud of

- **Holistic Monitoring:** Achieved a holistic monitoring solution that combines physiological data (Fitbit), digital activity tracking (ActivityWatch), and behavioral insights (eye tracking) to provide users with a comprehensive overview of their computer usage.

- **User-Friendly Interface:** Developed an intuitive and visually appealing interface using Streamlit, making it easy for users to navigate and interpret the collected data.

- **Personalized Feedback:** Successfully integrated GPT-4 for natural language feedback, allowing ALERT to offer personalized insights and suggestions based on the user's unique patterns and habits.

### What we learned

- **Interdisciplinary Integration:** Learned how to effectively integrate technologies from different domains, such as health monitoring, computer vision, and natural language processing, to create a cohesive and powerful tool.

- **Privacy Considerations:** Gained insights into the challenges and considerations involved in handling sensitive user data, especially when dealing with health-related information from devices like Fitbit or detailed system activity from ActivityWatch.

- **Real-time Processing Challenges:** Overcame challenges associated with real-time processing, enhancing our understanding of optimization techniques for responsive applications.

### What's next for ALERT

- **Enhanced Analytics:** Plan to expand the analytics capabilities, providing users with even more detailed insights into their productivity, focus levels, and overall well-being.

- **Machine Learning Refinement:** Continuously refine and improve machine learning models, including eye tracking and attentiveness detection, to enhance accuracy and reliability.

- **Extended Device Support:** Explore the integration of additional devices and sensors to broaden the scope of data collected, offering a more comprehensive understanding of user behavior.

- **User Customization:** Implement features that allow users to customize ALERT based on their specific goals, preferences, and workflow, ensuring a personalized and tailored experience.
