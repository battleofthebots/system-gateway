# System Gateway

Good news, we have finally added authentication to our power grid. Its officially unhackable™


## Description
System gateway is a small "power grid" website that has 2 major vulnerabilities that can be chained
to get RCE on the system. 

The vulns are based on the following techniques and CVEs:
1. [Default Credentials](https://attack.mitre.org/techniques/T0812/)
    - [CVE-2007-4361](https://nvd.nist.gov/vuln/detail/CVE-2007-4361)
        > "ReadyNAS RAIDiator before 4.00b2-p2-T1 beta creates a default SSH root password derived from the hardware serial number, which makes it easier for remote attackers to guess the password and obtain login access."
    - [CVE-2020-25753](https://nvd.nist.gov/vuln/detail/CVE-2020-25753)
        > "The default admin password is set to the last 6 digits of the serial number. The serial number can be retrieved by an unauthenticated user at /info.xml."
2. [Pickle Deserialization RCE](https://macrosec.tech/index.php/2021/06/29/exploiting-insecuredeserialization-bugs-found-in-the-wild-python-pickles/)
    - [CVE-2022-40238](https://nvd.nist.gov/vuln/detail/CVE-2022-40238)
        > "An authenticated attacker can inject arbitrary pickle object as part of a user's profile. This can lead to code execution on the server when the user's profile is accessed."
    - [CVE-2022-35411](https://nvd.nist.gov/vuln/detail/CVE-2022-35411)
        > "rpc.py through 0.6.0 allows Remote Code Execution because an unpickle occurs when the "serializer: pickle" HTTP header is sent."


## Building
To build the compiled python files, run the following command from the main directory. This copies the binaries from the builder.

```
build/build-binaries.sh
```


To run the server in the competition environment, use the following docker-compose file:

```yaml
version: '3'
services:
  system-gateway:
    build: .
    user: user
    restart: always
    ports:
      - "80:80"
```

> **Note**
> A local copy can also be run with the `docker-compose.yml` located in the directory by running `docker-compose up --build`

## Solve Script

To check for a solve run `python3 check/exploit.py`.

> **NOTE**
> There is a hardcoded port value of `80` in the script to match the Dockerfile, but if the solution is being run on a different port this will have to be changed.

## Releasing
To build a _release_ zip for the competitors to analyze, run the following command from the main directory. This release zip has everything the competitors need to run the server themselves and uses the "compiled" python instead of source code.

```
build/build-release.sh
```
