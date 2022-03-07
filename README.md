# Grader Extensions

This repository contains the lab/server extensions and the grader service as well as grader-convert.

The grader service has only been tested on Unix/macOS operating systems.

# Installation

This repository contains all the necessary packages for a full installation of the grader service.

- `grader-convert`: A tool for converting notebooks to different formats (e.g. removing solution code, executing, etc.). It can be used as a command line tool but will mainly be called by the service.
- `grading_labextension`: The JupyterLab plugin for interacting with the service. Provides the UI for instructors and students and manages the local git repositories for the assignments etc.
- `grader-service`: Manages students and instructors, files, grading and multiple lectures. It can be run as a standalone containerized service and can utilize a kubernetes cluster for grading assignments.


## Requirements

> JupyterHub, Python >= 3.8,
> pip,
> Node.js
> npm

# Manual Installation

## Local installation
Navigate to the `convert` directory and install the package requirements with the package manager `pip`

In the `grader` directory run:

    pip install ./convert
    pip install ./grading_labextension
    pip install ./grader_service

Then, navigate to the `grading_labextension`-directory and follow the instructions in the README file

## Running grader service
To run the grader service you first have to register the service in JupyterHub as an unmanaged service in the config:

    c.JupyterHub.services.append(
        {
            'name': 'grader',
            'url': 'http://127.0.0.1:4010',
            'api_token': '<token>'
        }
    )

You can verify the config by running `jupyterhub -f <config_file.py>` and you should see the following error message:
     
    Cannot connect to external service grader at http://127.0.0.1:4010. Is it running?


### Specifying user roles

Since the JupyterHub is the only source of authentication, the service has to rely on it to provide the necessary information. JupyterHub version 2.0 now supports RBAC which we will implement soon.

Until then, we rely on the group configuration of JupyterHub version 1.5. Users have to be added to specific groups which maps the users to lectures and roles. They have to be separated by double underscores.

The config could look like this:

    c.JupyterHub.load_groups = {
        "lect1__instructor": ["user1"],
        "lect1__tutor": ["user2"],
        "lect1__student": ["user3", "user4"]
    }

Here, `user1` is an instructor of the lecture with the code `lect1` and so on.

## Starting the service

In order to start the grader service we have to provide a configuration file for it as well:

    import os
    
    c.GraderService.service_host = "127.0.0.1"
    # existing directory to use as the base directory for the grader service
    service_dir = os.path.expanduser("<grader_service_dir>")
    c.GraderService.grader_service_dir = service_dir
    
    c.GraderServer.hub_service_name = "grader"
    c.GraderServer.hub_api_token = "<token>"
    c.GraderServer.hub_api_url = "http://127.0.0.1:8081/hub/api"
    c.GraderServer.hub_base_url = "/"

    c.LocalAutogradeExecutor.base_input_path = os.path.expanduser(os.path.join(service_dir, "convert_in"))
    c.LocalAutogradeExecutor.base_output_path = os.path.expanduser(os.path.join(service_dir, "convert_out"))

The `<token>` has to be the same value as in the JupyterHub token specified earlier. The `grader_service_dir` directory has to be an existing directory with appropriate permissions to let the grader service read and write from it.

Then we can start the grader service by specifying the config file as such:

    grader-service -f <grader_service_config.py>

When restarting the JupyterHub you should now see the following log message:

    Adding external service grader at http://127.0.0.1:4010

Do not forget to set the log level to `INFO` in the JupyterHub config if you want to see this message.

