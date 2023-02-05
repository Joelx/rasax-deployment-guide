<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!--
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]
-->


<!-- PROJECT LOGO -->
<br />
<!--
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>
-->
  <h3>RASA (X) Deployment Guide</h3>

  <p>
Rasa Open Source is a fantastic project and arguably the most accessible chatbot framework. However, deploying Rasa and Rasa X in a "live"/production environment presents some pitfalls. Amongst many reasons, the deployment variants via Docker Compose and Quick Install Script are deprecated for Rasa 3. And the latter used the cluster distribution KIND anyway, which is nominally not production-ready. 
</p>
<p>
The recommended method of installation via the Rasa X Helm Chart (https://github.com/RasaHQ/rasa-x-helm) works quite well out-of-the-box. However, configuring a realistic use case for a production-ready deployment can still be quite difficult. In addition, it is intended for use on cloud servers with a managed load balancer. 
</p>
<p>
But there are reasons why you wouldn't want to deploy your chatbot on a cloud server. You may work for a (European) University or another authority that won't allow you to host your project on an AWS or Azure server for example. My own projects so far have always required deploying Rasa (X) on a self-hosted server and making it available to a small to medium sized audience via a web service. 
</p>
<p>
The endeavour of deploying Rasa and Rasa X has gotten even more complicated since summer 2022, because Rasa X is no longer supported in the free version. I just haven't found a really suitable and simple guidance to install and configure a Rasa and Rasa X deployment for my use case. That's why I decided to share my deployment method with you as a STEP-BY-STEP Guide, using the most recent compatible FREE versions of Rasa Open Source and Rasa X. 
</p>


This repository is for you if you
<ul>
    <li>are frustrated because you just can't get Rasa (X) to deploy properly</li>
    <li>want to install Rasa (X) on an Ubuntu server</li>
    <li>want to have more control over your deployment</li>
    <li>would like to make your chatbot accessible via a website/web service</li>
    <li>have a small to medium sized project and would like to use a single server for your web services, Rasa and Rasa X.</li>
</ul>

Since I tried to document every step, no matter how trivial it may seem, this guide should also be escpecially suitable for Kubernetes newbies.<br>

It's <b>NOT</b> for you, if you would like to deploy your Rasa (X) on an external LoadBalancer with the bundled nginx Service of the Rasa X Helm Chart deactivated. However, even then this could be a starting point if you are new to Rasa (X) deployments and just want to get started.


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    <!--  <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul> -->
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li>
        <a href="#installation">Guide</a>
          <ul>
              <li><a href="#microk8s-cluster-setup">microk8s cluster setup</a></li>
              <li><a href="#prepare-configuration-files-and-folder-structure">Prepare configuration files and folder structure</a></li>
              <li><a href="#rasa-x-helm-chart">Rasa X Helm Chart</a></li>
              <li><a href="#integrate-and-train-model">Integrate and train model</a></li>              
              <li><a href="#kubernetes-dashboard">Kubernetes Dashboard</a></li>
              <li>
              <a href="#create-a-webservice-to-host-your-chatbot">Create a Webservice to host your Chatbot</a>
                <ul>
                  <li><a href="#build-webservice">Build Webservice</a></li>              
                  <li><a href="#deploy-webservice">Deploy Webservice</a></li>
                </ul>
              </li>
              <li><a href="#activate-ssltls">Activate SSL/TLS</a></li>
              <li>
                <a href="#action-server">Action Server</a>
                <ul>
                  <li><a href="#cicd-github-workflow">CI/CD GitHub Workflow</a></li>
                </ul>
              </li>
          </ul>
        </li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
   <!-- <li><a href="#contact">Contact</a></li> -->
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

This guide explains how to build a Rasa Open Source and Rasa X production deployment on a "bare-metal" Ubuntu (root) Server. The repository contains all necessary configuration files, as well as a Rasa Demo-Bot and a Demo-Website. You can either use specific configurations as a reference for your own deployment, or you can follow this guide step-by-step. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!--

### Built With

* [![Rasa][Rasa]][Rasa-url]
* [![RasaX][RasaX Helm Chart]][RasaX-helm-url]
* [![microk8s][microk8s.io]][Microk8s-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>

-->

<!-- GETTING STARTED -->
## Getting Started

I would recommend starting with a freshly installed Ubuntu machine. However, if you have other tasks running on your machine, please be aware that following this setup may interfere with your network services.

### Prerequisites

1. Install snapd packaging system, Docker and microk8s cluster distribution:
  ```sh
  sudo apt update
  sudo apt install snapd
  sudo apt install docker.io docker-compose
  ```

## Guide

### microk8s cluster setup

1. Install microk8s via snap:
```sh
sudo snap install microk8s --classic
```

1. Add microk8s user to avoid sudo:
```sh
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
```

1. Enable microk8s addons:
```sh
microk8s enable dns storage helm3 registry dashboard ingress
```  

<i>Explanations: </i> <br>
<b>dns:</b> enable DNS and service discovery between pods<br/>
<b>storage:</b> enable dynamic volume storage provisioning<br/>
<b>helm3:</b> enable helm package manager<br/>
<b>registry:</b> enable container registry to store and distribute images<br/>
<b>dashboard:</b> enable Kubernetes Dashboard<br/>
<b>ingress:</b> enable ingress(-nginx) to make cluster reachable externally <br/>

4. Apply kube config:
```sh
cd $HOME/.kube
microk8s config > config
```

5. Register alias for microk8s.kubectl and microk8s.helm3:
```sh
sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm3 helm
```

### Prepare configuration files and folder structure

To follow this guide step-by-step I would recommend to clone this repository. All of the upcoming commands assume you are in the root directory of this project:
```sh
git clone git@github.com:Joelx/rasax-deployment-guide.git
cd rasax-deployment-guide
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Rasa X Helm Chart
1. Create a namespace for our deployment (in this case I chose `rasax`):
```sh
kubectl create namespace rasax
```
2. Clone official Rasa X Helm Chart repository:
```sh
helm repo add rasa-x https://rasahq.github.io/rasa-x-helm
```
3. Head over and edit the `rasax/basic-values.yml` file. Specify the external IP address of your server and generate a random string for each of the secret and token properties. (You can take hints from the values.yaml files about what exactly you have to enter into the respective fields)<br>

4. Add the official Rasa X Helm Chart to your repositories:
```sh
helm repo add rasa-x https://rasahq.github.io/rasa-x-helm
```

5. Install the Helm Chart into our namespace. Note that we also chose a custom release name `rasax-release`:
```sh
helm --namespace rasax install --values rasax/basic-values.yml rasax-release rasa-x/rasa-x
```
6. Now the best part after installing a Helm Chart! Go ahead and check how your containers are creating and your pods are coming into life:
```sh
kubectl -n rasax get pods
```

![Pods of Rasa X Helm Chart Creating][Pod1-image]
<br>

7. Likewise you can check the services and see what ports are being used.:
```sh
kubectl -n rasax get pods
```
![Services registered in our namespace ][Services1-image]

<br/>
If all pods are running and everything is properly configured, you should be able to reach the Rasa X GUI by accessing http://YOUR.IP.ADDRESS:8000 in your browser: <br>
<br>

![Rasa X Login Screen][RasaxLogin-image]
<br>

You can log into the admin interface with the username `admin` and the string you specified as your password through the `rasax.initialUser.password` field in your `basic-values.yaml`.
<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Integrate and train model

There are multiple ways to load and use Rasa models. You could e.g. connect an external Rasa Open Source service to your deployment or you could use a model storage. However, in this case we use Rasa X with GitHub integration to manage our models.<br> 
After logging into your Rasa X admin interface, head over and connect the GitHub repository containing your chatbot configuration. If you follow this guide step-by-step, you should already have cloned or forked this repistory. You can now connect your clone/fork with Rasa X. You can do this via the admin GUI and it is pretty straightforward. It will give you a SSH Key, which you have to provide to your GitHub account. <br/>
<br/>
After you have connected your GitHub account, Rasa X will synchronize your chatbot configuration. This can sometimes take a couple of minutes. If your configuration has been loaded successfully, you can train and activate your model from the Rasa X interface. <br>
<br>
<b>Troubleshooting</b><br>
If Rasa X either fails to load your chatbot configuration or fails training, more often then not the problem is caused by some misconfiguration of your chatbot configuration files (domain.yml, stories.yml, etc.). You can check them with a YAML Checker like yamllint (https://www.yamllint.com/). One very common problem is also having the wrong version specified in your configuration files. It's usually the first line (e.g. `version: "3.0"`) in your .yaml files. Rasa X is rather strict with this.<br>
<br>
One common problem with failed training is also caused by a missing "rasa-worker" - pod. However, unfortunately Rasa X is rather opaque when it comes to error messages. For troubleshooting you need to take a look into the logs of your pods. Because pods are ephemeral and have no static name, you would first need to look up the current pod name with `kubectl -n rasax get pods` if you want to do it with kubectl. In this case, we would need the exact name of the "rasax-release-rasa-x" - and the "rasax-release-rasa-worker" -Pod. You could then e.g. go with `kubectl -n rasax logs rasax-release-rasa-x-647c9c7d5-2l79d -f` and follow your logs. However, this procedure is rather tedious... this is where a Kubernetes Dashboard comes in really handy! We will discuss it in the next section.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Kubernetes Dashboard
Remember we already activated the Kubernetes Dashboard via `microk8s enable dashboard` earlier? All you have to do is open a second terminal session and type in:
```sh
microk8s dashboard-proxy
```
Copy the token you are given and head over to `http://YOUR.IP.ADDRESS:10443` in your Browser. When prompted, paste the token to log into the Kubernetes dashboard that is automatically connected to your cluster via microk8s. You can select the `rasax` namespace on the top left. Then on the left under "workload" you can select "pods". To view the logs, go to one of the pods via clicking it's name and then in the top right hand corner click on that "hamburger-menu-esque" symbol.<br>

![Kubernetes Dashboard Logs][ks-dashboard-logs-image]
<br><br>

 Often times its beneficial to enable auto-refresh. You can do this via the Kebab menu on the right. <br>

 ![Kubernetes Dashboard auto-refresh][ks-dashboard-logs-ar-image]
 <br>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Create a Webservice to host your Chatbot
In order to host a Rasa chatbot through a website, we need to have a
- [x] REST or WebSocket interface that our Rasa worker/production Pods listen to.
- [ ] website with a chatbot widget that communicates with this interface.
- [ ] web service that serves our website

We already enabled REST and WebSocket channels in our `basic-values.yml`. The next part is to deploy a webservice. For that, I've prepared a demo Website for you. You can find it in the `website/` directory. I'm using a slightly adjusted version of the rasa-webchat widget by botfront (https://github.com/botfront/rasa-webchat) which supports WebSocket. Another really great widget is made by JiteshGaikwad (https://github.com/JiteshGaikwad/Chatbot-Widget), which however uses the REST webhook channel. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

#### Build Webservice
In this case we won’t push our image to a remote registry like Docker Hub. Instead we store it locally. However, there’s a little trickery required (https://microk8s.io/docs/registry-images). Note that we're using the image tag `:local`. You can choose another tag name if you like, but due to the way the microk8s image registry works, you can't use the `:latest` tag.<br>
<br>
1. Build the website image:
```sh
docker build website/. -t  rasa-webservice:local -f website/Dockerfile
```
2. Store the image on your filesystem:
```sh
docker save rasa-webservice > rasa-webservice.tar
```
3. Import the image to the local microk8s:
```sh
docker save rasa-webservice > rasa-webservice.tar
```
4. Confirm that the image has been imported:
```sh
microk8s ctr images ls
```
You can now remove the `rasa-webservice.tar` on your filesystem if you like. 
Feel free to simply use a remote registry instead. In this case, make sure to edit the `k8s-configs/website-deployment.yaml` to reference your username for Docker Hub. 

#### Deploy Webservice
Because the k8s LoadBalancer works on Layer 7, you need a Domain Name that points to the external IP Address of your server for the next step. Alternatively you can use services like https://nip.io/. 
<br><br>
1. Head over to the `k8s-configs/basic-webservice.yaml`. Replace EXAMPLE.COM with your domain name in the Ingress configuration under `spec.rules.host`.<br>

2. Apply the k8s configuration for deployment, service and ingress of your webservice:
```sh
kubectl apply -f k8s-configs/basic-webservice.yaml
```

That's it! You should now be able to access your chatbot via browser!

![Rasa Chatbot Widget][RasaChatbotWidget-image]


Perfect! Now we have a Cluster with a working Webservice that is reachable via http and connects to our Rasa deployment through WebSocket. 
If that is all you need (e.g. for a test- or intranet solution) you are ready to go. For a somewhat solid production environment, however, we need some more steps.


<p align="right">(<a href="#readme-top">back to top</a>)</p>


### Activate SSL/TLS

1. Enable cert-manager. Rather pleasantly it's integrated into microk8s as an addon!
```sh
microk8s enable cert-manager
```
2. Edit the `k8s-configs/tls-webservice.yaml` and replace the EXAMPLE.com entry with your correct domain name. Also very importantly you have to enter a valid e-mail address under the spec.acme.email field of the ClusterIssuer. Let's Encrypt will reject requests with @example.com e-mail addresses.<br>

3. Apply the new config. Additionally we're configuring a ClusterIssuer that issues a certificate from Let's Encrypt. Note that the ingress of our "basic-webservice" gets overwritten with that command: 
```sh
kubectl apply -f k8s-configs/tls-webservice.yaml
```

4. Now a certificate is getting issued from Let’s Encrypt. You can view the status via:
```sh
kubectl describe certificate rasa-webservice-ingress-tls -n rasax
```

![Certificate][Certificate-image]

This certificate gets managed and auto updated just like it would with cert-bot. After the certificate has been issued successfully, you should be able to visit your webservice via https://YOUR-DOMAIN.com . However, since the Rasa Deployment isn’t configured for TLS, the WebSocket Connection to Rasa will be broken due to a CORS conflict.<br><br>

Now there are multiple ways to configure SSL/TLS for the Rasa (X) deployment. Ideally you would configure a `customConfConfigMap` and the `certificateSecret` and mount the certificate in the nginx pod of your Rasa X deployment. I have included an example configuration for the ConfigMap under `custom-nginx-conf-files` to get you started. Maybe in the future I will cover that. However, today we wanna use the simplest working solution. And this is to use our ingress to route traffic over TLS to the nginx backend service of our Rasa X deployment. 

1. Edit the `rasax/tls-values.yml` and enter your IP address and domain name. You must also transfer the random tokens and secret strings from the basic-values.yml. <br>

2. Upgrade your deployment with the new values file:
```sh
helm --namespace rasax upgrade --values rasa/tls-values.yml rasax-release rasa-x/rasa-x
```

<b>Note that we are now hosting our API under the /rasax/ subpath!</b> That means, that your Rasa (X) services will be reachable via https://YOUR-DOMAIN.com/rasax/ while your Chatbot Website will still run under https://YOUR-DOMAIN.com/ ! For me thats a reasonable configuration, but feel free to adjust this to your needs. However, those changes would also need to be reflected in the ingress and on your webservice that we will discuss now.<br>

3. Head over to the `k8s-configs/rasax-ingress-tls-controller.yaml` and, again, edit it to reflect your actual domain name.<br>

4.  Apply the new ingress rule:
```sh
kubectl apply -f k8s-configs/rasax-ingress-tls-controller.yaml
```

Now we have configured TLS for the ingresses of our webservice and for traffic to Rasa (X). We now need to rebuild our webservice to reflect the new API. 

5. Go to your `website/index.html` and edit the JavaScript. Note the comments in that file for guidance. After editing, it should look somewhat like this:
```js
        !(function () {
         let e = document.createElement("script"),
        t = document.head || document.getElementsByTagName("head")[0];
        (e.src =
        "static/js/webchat.js"),
        (e.async = !0),
        (e.onload = () => {
        window.WebChat.default(
        {
          initPayload: '/greet',
          customData: { language: "en" },
          socketUrl: location.hostname,
          socketPath: "/rasax/socket.io/",
          title: 'My Chatbot',
          subtitle: 'My Subtitle',
          profileAvatar: "static/images/sara_avatar.png",
          inputTextFieldHint: 'Type here...',
        },
        null
      );
        }),
        t.insertBefore(e, t.firstChild);           
    })();

```

Note that we ditched the port :8000 and added our socketPath to reflect the new API location. The nginx pod of our Rasa X deployment works as a reverse proxy and automatically redirects the traffic coming over the /socket.io path to the Rasa Production pod in our cluster at `http://rasax-release-rasa-x-rasa-production.rasax.svc:5005/socket.io`.<br>
<br>
<b>Also note that you will need a trailing slash (/) when accessing your services!</b> So for example you have to type https://YOUR-DOMAIN.com/rasax/ (with trailing slash!) into your browser to access the Rasa X GUI. Wether you can live with that depends on what you are trying to accomplish. If you want to change this behaviour, you would need to reconfigure the ingress controller and your nginx. A good starting point may be this medium.com article: https://medium.com/@smoco/fighting-trailing-slash-problem-c0416023d20e . <br>
<br>

6. After adjusting our index.html, we need to rebuild the webservice:
```sh
docker build website/. -t  rasa-webservice:local -f website/Dockerfile

docker save rasa-webservice > rasa-webservice.tar

microk8s ctr image import rasa-webservice.tar
```

7. We now need to force Kubernetes to re-pull the new image. For that, we first delete our existing deployment:
```sh
kubectl -n rasax delete deployment rasa-webservice
```

8. In the name of clarity, I bundled deployment, service and ingress of our Webservice in that one file (`basic-webservice.yaml`) we used earlier. We then overwrote the ingress controller with another file (`tls-webservice.yaml`). Because of that, we can't use the basic-webservice.yaml anymore to re-build our deployment. That's why I have prepared another file for that: `webservice-deployment.yaml`. I hope I didn't confuse you now ;) <br> Just go ahead and apply it:
```sh
kubectl apply -f k8s-configs/webservice-deployment.yaml
```

Now your webservice pod should have been rebuilt using the new image allowing your website to reach out to the new API location. 

### Action Server 
More often then not you also want to have an Action Server allowing you to run custom actions in your Rasa deployment. In this section, I will show you how to enable the action server in your Rasa X deployment, build an action server image and get you started with a mini CI/CD workflow that allows you to automate your action server image building. <br>
<br>

1. This time we wanna use Docker Hub for the sake of our CI/CD workflow. So first make sure you are logged into docker hub on your terminal:
```sh
docker login
```
2. (Optional) You could also skip this part and build it from your CI/CD workflow directly. In this case we first build our action server via a Dockerfile provided under the root directory of this project:
```sh
docker build . -t YOUR-DOCKER-HUB-USERNAME/example-action-server:latest
```
3. (Optional) Push to docker hub:
```sh
docker build . -t YOUR-DOCKER-HUB-USERNAME/example-action-server:latest
```
4. (Required) Edit `rasax/tls-values-with-actions.yml` to reflect your IP, domain and token + secret strings. <br>
   <br>
5. (Optional) Upgrade your Rasa X deployment with the new values:
```sh
helm --namespace rasax upgrade --values rasax/tls-values-with-actions.yml rasax-release rasa-x/rasa-x
```
6. (Optional) Check that your action server pod is creating/running:
```sh
kubectl -n rasax get pods
```
![Action Server Pod Creating][ActionServerPod-image]

You can check wether the action is working via the chatbot widget in your browser (note the actions.py and the rule I added for the example bot provided in this repository):

![Action Server Test 1][ActionServerTest1-image]

#### CI/CD GitHub Workflow
Building and deploying the action server like in the previous section can be quite tedious. Everytime you make changes to the code of your action server, you would manually need to re-build your image. Thankfully we can automate that with GitHub Workflows!

1. Head over to the `.github/workflows/action_server_image.yml` file and fill in your docker hub username. Also make sure that the correct branch name is configured (e.g. main).<br>
   <br>
2. Don't forget to update the secrets inside your GitHub account repository to store the DOCKER_HUB_LOGIN and DOCKER_HUB_PASSWORD. You can find those settings on your GitHub Account, inside your Repository settings under Settings -> Security -> Secrets and variables -> Actions -> New repository secret. It should look something like that:

![Create a GitHub Secret for Docker Hub Login][DockerHubLogin-image]

3. (Optional) If you have already deployed your action server with the Dockerfile in the section above, you could now make a small change to your action server code to test your workflow. So e.g. in your actions.py, add another utterance: 
  
![Action Server Test 2][ActionServerTest2-image]

4. Push the actions to your repository:
```sh
git add actions/.

git commit -m "Added another dispatcher message in actions.py"

git push
```

5. You can follow the building process on your GitHub account under the "Actions" tab:

![GitHub Action Building][github-action-building-image]

6. Now we have to update the action server pod to store our new image. Therefore we need to specify the new image in our deployment. After pushing the action changes to your repo and thus triggering your Github Action, head over to Docker Hub and get your Image Tag. 

![Get image tag from docker hub][docker-hub-image-tag-image]

7. Now back in your `rasax/tls-values-with-actions.yml` go ahead and update the image tag:

![Enter image tag in values.yml][values-yaml-image-tag-image]

8. Upgrade your Rasa X deployment:
```sh
helm --namespace rasax upgrade --values rasax/tls-values-with-actions.yml rasax-release rasa-x/rasa-x
```

Admittedly updating your image tag like this is still a bit tedious. I suppose you could automate that too, but personally I didn't really need it yet. Have a look at https://rasa.com/docs/action-server/deploy-action-server/#building-an-action-server-image if you're interested. There are also some nice examples on the official Rasa X documentation, if you want to optimize your workflow further: https://rasa.com/docs/rasa/setting-up-ci-cd/ . 



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments


* [DLMade on medium.com](https://medium.com/analytics-vidhya/rasa-advanced-deployment-part-1-installation-51d660e0367b)
* [RasaHQ](https://rasa.com/)
* [othneildrew Readme Template](https://github.com/othneildrew/Best-README-Template)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Rasa-url]: https://rasa.com/
[Microk8s-url]: https://microk8s.io/
[RasaX-helm-url]: https://github.com/RasaHQ/rasa-x-helm

[Pod1-image]: images/pods1.png
[Services1-image]: images/services1.png
[RasaxLogin-image]: images/rasax-login.png
[ks-dashboard-logs-image]: images/view-logs.png
[ks-dashboard-logs-ar-image]: images/auto-refresh.png
[RasaChatbotWidget-image]: images/chatbot-widget.png
[Certificate-image]: images/certificate.png
[ActionServerPod-image]: images/action-server-building.png
[ActionServerTest1-image]: images/action-test-1.png
[DockerHubLogin-image]: images/github-secrets-dh-user.png
[ActionServerTest2-image]: images/action-server-code-change.png
[github-action-building-image]: images/gh-action-building.png
[docker-hub-image-tag-image]: images/dh-image-tag.png
[values-yaml-image-tag-image]: images/values-yaml-image-tag.png

[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white

[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 