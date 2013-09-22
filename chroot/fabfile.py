from fabric.api import *
from time import sleep

env.hosts = ["root@192.168.56.101"]
env.vmname = "lfs"
env.sourcepath = "/sources"
env.lfsroot = "/mnt/lfs"
env.partition = "/dev/sda3"

CHROOT_CMD = (
        'chroot "%s" /tools/bin/env -i '
        'HOME=/root '
        'TERM="$TERM" '
        "PS1='\u:\w\$ ' "
        'PATH=/bin:/usr/bin:/sbin:/usr/sbin:/tools/bin '
        'bash --login +h')


def build(pkg, script):
    start()
    buildpkg(pkg, script)
    finish(pkg)


def start():
    startvm()
    prepare()


def buildpkg(pkg, buildscript):
    real_path = '%s/tmp/build_%s' % (env.lfsroot, pkg)
    chroot_path = '/tmp/build_%s' % pkg

    decompress(pkg)
    put(buildscript, real_path, mode=0777)
    run_chroot(chroot_path)
    run("rm %s" % real_path)


def finish(pkg):
    cleanup(pkg)
    stopvm()
    snapshot(pkg)


def startvm():
    local("VBoxManage startvm %s" % env.vmname)
    print("waiting for vm to boot")
    sleep(35)


def prepare():
    run("mount -t ext4 %s %s" % (env.partition, env.lfsroot))
    run("mount -v --bind /dev %s/dev" % env.lfsroot)
    run("mount -vt devpts devpts %s/dev/pts" % env.lfsroot)
    run("mount -vt proc proc %s/proc" % env.lfsroot)
    run("mount -vt sysfs sysfs %s/sys" % env.lfsroot)
    run("mount -vt tmpfs shm %s/dev/shm" % env.lfsroot)


def decompress(pkg):
    with cd("%s%s" % (env.lfsroot, env.sourcepath)):
        run("tar xf %s.tar.*" % pkg)


def run_chroot(scriptpath):
    chroot_cmd = CHROOT_CMD % env.lfsroot
    return run('%s %s' % (chroot_cmd, scriptpath))


def cleanup(pkg):
    path = pkgpath(pkg)
    run("rm -R %s" % path)


def pkgpath(pkg):
    return "%s%s/%s" % (env.lfsroot, env.sourcepath, pkg)


def stopvm():
    local("VBoxManage controlvm %s acpipowerbutton" % env.vmname)
    print("waiting for vm to stop")
    sleep(10)


def snapshot(pkg):
    pkgname = pkg.rpartition("-")[0]
    local("VBoxManage snapshot %s take %s" % (env.vmname, pkgname))
