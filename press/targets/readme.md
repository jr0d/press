Press post image

Goals:
	modular
	extensible
	fast
	integrated post processors use the same interface as plugin processors

Decorators are used to declaratively define post tasks
	post.run(target=TargetKlass)
	post.chroot(taget=TargetKlass)

		class Target(object):
			__inherit = List()

		class Linux(Target):
			?????


Target hierarchy:

	Linux
	
		|_ Debian
		
				|_ Ubuntu ?
				
						|_ == U12_04, >= U12_04
						
						|_ U14_04 



Essentially we want to be able to define jobs that are only applied to the correct target. If the target is Linux then
it will be applied to everything that inherits from the Linux target class. I am not sure if we should use the mro or
our own inheritance tracking. Press will inspect the image and know how to determine what jobs to apply: for instance,
it will use lsb_release and store the version information. It will then prune the jobs list of any jobs that do not
match

Job dependencies, order, and priority. Should jobs be independent? ie, having an auth job which handles all user/group
creation? Or should there be a way to dictate job run order.

Should I look into using salt or some configuration management software? Jobs would then be defined in an out of code
syntax, which could be helpful, but may also introduce to much overhead... NO, press post actions should only 
configure: auth, networking, bootloader, and configuration management software. 

Common libraries for dealing with common systems: SYSV init, upstart, systemd ??
Options for consistent interface naming: udev, biosdevname, net.ifnames

----

Fast forward a year or so:

The post install target class hierarchy will be traversed at runtime all classes will be registered. After image
deployment, press will iterate over all registered classes attempting to match Target.name with
press_configuration[target]. If target is specified and no post install target is matched, an error will be raised.
If press_configuration[target] is None, press will will run each classes probe method and return the last class where
Target.probe is True. For instance, if Linux.probe and redhat.probe are True and rhel6/7, fedora, centos are all false,
target redhat will be used.

Extending:
Plugins may import a base class, override, and extend methods and then call register_target. Plugin registered targets
will be scanned by press after supported target classes, ensuring that the plugin classes have priority

---

v0.5 update: This will be replaced by a Task() Manifest() model. The primary reason for the shift in thinking is the
ability to easily add in Task order and dependency enforcement, rather than relying on mro and class overrides.