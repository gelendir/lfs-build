from fabric.api import *
from time import sleep

env.hosts = ["lfs@192.168.56.101"]
env.vmname = "lfs-atelier2"
env.sourcepath = "/sources"
env.lfsroot = "/mnt/lfs"
env.partition = "/dev/sda3"
env.shell = "/bin/bash -c"


def build(pkg, script):
    startvm()
    buildpkg(pkg, script)
    finish(pkg)


def startvm():
    local("VBoxManage startvm %s" % env.vmname)
    print("waiting for vm to boot")
    sleep(35)


def buildpkg(pkg, scriptpath):
    decompress(pkg)

    remotepath = '/tmp/build_%s' % pkg

    put(scriptpath, remotepath, mode=0777)
    run(remotepath)
    run("rm %s" % remotepath)


def finish(pkg):
    cleanup(pkg)
    snapshot(pkg)


def decompress(pkg):
    path = "%s%s" % (env.lfsroot, env.sourcepath)
    with cd(path):
        run("tar xf %s.tar.*" % pkg)


def cleanup(pkg):
    path = pkgpath(pkg)
    run("rm -R %s" % path)


def pkgpath(pkg):
    return "%s%s/%s" % (env.lfsroot, env.sourcepath, pkg)


def snapshot(pkg):
    pkgname = pkg
    local("VBoxManage snapshot %s take %s" % (env.vmname, pkg))
    local("VBoxManage controlvm %s resume" % (env.vmname,))
