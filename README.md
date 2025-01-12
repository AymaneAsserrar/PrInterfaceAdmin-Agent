# **Monitoring Agent ia-groupe-8**

## About the project

The IA Group 8 Monitoring Agent is a Python-based solution designed to retrieve key system metrics such as CPU usage, RAM usage, disk activity, and error detection in logs. The agent works by gathering data in real-time and exposing it through an API. 

## Prerequisites

Before you continue, ensure you have met the following requirements:

- **Python 3.X**: Programming language for the application
- **virtualenv**: To create isolated Python environments [intall](https://virtualenv.pypa.io/en/latest/installation.html)
- **Uvicorn**: ASGI server for running FastAPI applications
- **Psutil**: System monitoring library for CPU, RAM, and disk usage
- **Click**: A package for creating command-line interfaces
- **Apache Log Parser**: For parsing and analyzing Apache logs


## How to install the project

- **Clone the project**:
```sh
  git clone git@devops.telecomste.fr:printerfaceadmin/2024-25/group8/ia-groupe-8.git
  cd ia-groupe-8
```

- **Activate a virtual environment**:
```sh
  python3 -m venv venv
  source venv/bin/activate
```

- **Install the dependencies**:
```sh
  pip install -r requirements.txt
  pip install -r requirements.dev.txt
```

## How to use the project
- **Start the application**:
```sh
  make run
```

- **Debug the application**:
```sh
  make debug
```

- **Exit the application**:
```sh
  ctrl + C
```
## Badges

You will find below the badges for the pipeline status and the test coverage, providing insights into the project's build health and code quality.


![pipeline status](https://devops.telecomste.fr/printerfaceadmin/2024-25/group8/ia-groupe-8/badges/main/pipeline.svg)
![coverage report](https://devops.telecomste.fr/printerfaceadmin/2024-25/group8/ia-groupe-8/badges/main/coverage.svg)

## How to contribute to the project

- **Clone the project**:
```sh
  git clone git@devops.telecomste.fr:printerfaceadmin/2024-25/group8/ia-groupe-8.git
  cd ia-groupe-8
```

- **Create a branch**:
```sh
  git checkout -b my-awesome-feature
```

- **Make amazing changes!**:
Fix bugs, add features, or even update the README because good documentation makes everything better.

- **Submit a merge request:**:
Push your changes, describe what you did, and open a merge request with a nice description. We love descriptions.


## Contributors

We wouldn’t be here without the contributions of these brilliant minds:  
-ASSERAR Aymane  
-EL-KOULFA Hassane  
-GOUHIER Matteo  
-HARGANE Chayma  
-TIDJANI MOHAMED Archou  

Want to see your name here? Check out the section above to learn how to contribute!

## Acknowledgements

Special thanks to:

Mehdi Zeghdallou, Damien Jacinto and Jules Chevalier: Our three professors who showed incredible patience and support throughout this project.

## License

No specific license has been assigned to this project.
For questions regarding usage or rights, please contact the authors.

