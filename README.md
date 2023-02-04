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
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">RASA (X) Deployment Guide</h3>

  <p align="center">
Rasa Open Source is a fantastic project and arguably the most accessible chatbot framework. However, deploying Rasa and Rasa X in a "live"/production environment presents some pitfalls. However, the deployment variants via Docker Compose and Quick Install Script are deprecated for Rasa 3. The latter used the cluster distribution KIND anyway, which is nominally not production-ready. 

The meanwhile recommended method of installation via helmet chart works quite well out-of-the-box. However, configuring a realistic use case for a production-ready deployment can be quite difficult. In addition, it is intended more for use on cloud servers with a managed load balancer. 

My own projects so far have always required deploying Rasa (X) on a self-hosted server and making it available to a small to medium sized audience via a web service. I just haven't found a really suitable and simple guide for this.

The situation has gotten even worse since summer 2022, because Rasa X is no longer supported in the free version. So I tried to use the latest compatible and free versions.

This repository is for you if you
<ol>
    <li>are frustrated because you just can't get Rasa (X) to deploy properly</li>
    <li>want to install Rasa (X) on a "normal" Ubuntu server</li>
    <li>want to have more control over your deployment</li>
    <li>would like to make your chatbot accessible via a website/web service</li>
    <li>have a small to medium sized project and would like to use a single server for Rasa and Rasa X.</li>
</ol>
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/othneildrew/Best-README-Template">View Demo</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Report Bug</a>
    ·
    <a href="https://github.com/othneildrew/Best-README-Template/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This guide explains how to build a Rasa Open Source and Rasa X production deployment on a "bare-metal" Ubuntu (root) Server. The repository contains all necessary configuration files, as well as a Rasa Demo-Bot and a Demo-Website. You can either use specific configurations as a reference for your own deployment, or you can follow this guide step-by-step. 

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![Rasa][Rasa]][Rasa-url]
* [![React][React.js]][React-url]
* [![Vue][Vue.js]][Vue-url]
* [![Angular][Angular.io]][Angular-url]
* [![Svelte][Svelte.dev]][Svelte-url]
* [![Laravel][Laravel.com]][Laravel-url]
* [![Bootstrap][Bootstrap.com]][Bootstrap-url]
* [![JQuery][JQuery.com]][JQuery-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

I would recommend starting with a freshly installed Ubuntu machine. However, if you have running other tasks on your machine, please be aware that following this setup may interfere with your networking services.

### Prerequisites

1. Install snapd packaging system, Docker and tge microk8s cluster distribution
  ```sh
  sudo apt update
  sudo apt install snapd
  sudo apt install docker.io docker-compose
  ```

### Guide
#### microk8s cluster setup
_Below is an example of how you can instruct your audience on installing and setting up your app. This template doesn't rely on any external dependencies or services._
1. Install microk8s via snap
```sh
sudo snap install microk8s --classic
```
2. Add microk8s user to avoid sudo 
```sh
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
```
3. Enable microk8s addons.  
```sh
microk8s enable dns storage helm3 registry dashboard ingress
```  
<b>dns:</b> enable DNS and service discovery between pods<br/>
<b>storage:</b> enable dynamic volume storage provisioning<br/>
<b>helm3:</b> enable helm package manager<br/>
<b>registry:</b> enable container registry to store and distribute images<br/>
<b>dashboard:</b> enable Kubernetes Dashboard<br/>
<b>ingress:</b> enable ingress(-nginx) to make cluster reachable externally <br/><br/>
4. Apply kube config
```sh
cd $HOME/.kube
microk8s config > config
```
5. Register alias for microk8s.kubectl and microk8s.helm3
```sh
sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm3 helm
```

#### Prepare configuration files and folder structure
* To follow this guide step-by-step I would recommend to clone this repository. All of the upcoming commands assume you are in the root directory of this project. 
```sh
git clone git@github.com:Joelx/rasax-deployment-guide.git
cd rasax-deployment-guide
```

#### Rasa X Helm Chart
1. Create a namespace for our deployment (in this case I chose <i>rasax</i>)
```sh
kubectl create namespace rasax
```
2. Clone official Rasa X Helm Chart repository
```sh
helm repo add rasa-x https://rasahq.github.io/rasa-x-helm
```
3. Install the Helm Chart into our namespace. Note that we also chose a custom release name: <i>rasax-release</i>.
```sh
helm --namespace rasax install --values rasax/basic-values.yml rasax-release rasa-x/rasa-x
```
4. Now the best part after installing a Helm Chart! Go ahead and check how your containers are creating and your pods are coming to life!
```sh
kubectl -n rasax get pods
```
[![Pods of Rasa X Helm Chart Creating][Pod1-image]]
5. Likewise you can check 
```sh
kubectl -n rasax get pods
```
[![Pods of Rasa X Helm Chart Creating][Service1-image]]

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Install NPM packages
   ```sh
   npm install
   ```
4. Enter your API in `config.js`
   ```js
   const API_KEY = 'ENTER YOUR API';
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Rasa-url]: https://rasa.com/
[Pod1-image]: images/pods1.png
[Services1-image]: images/services1.png

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