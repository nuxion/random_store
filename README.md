# Random Store

It is a distributed content based store. 

At first digested for small to medium values. This project is inspired by different projects and tecnologies.

The main inspiration is [minikeyvalue](https://github.com/nuxion/minikeyvalue) which in turn is based on [Seaweedfs](https://github.com/chrislusf/seaweedfs)

The principal idea is a central coordinator, backed by a [Redis](https://redis.io/) instance, which enrutes requests to a specific Volume server, backed by a [Nginx](https://www.nginx.com/) instance.

A main difference with [minikeyvalue](https://github.com/nuxion/minikeyvalue) is that each file will have asigned a path related to their content, using a [cryptographic hashing function](https://en.wikipedia.org/wiki/Cryptographic_hash_function), similar to how [solutions like IPFS and Filecoin works](https://proto.school/), also similar to [Perkeep](https://perkeep.org/)


## Status

**~Alpha** in development

## Resources

see [here](resources.md)


## License
see [here](LICENSE.rst)


