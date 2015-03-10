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