# Hooks

Hooks are designed to allow press developers inject arbitrary code into the press process.

Hooks are a function that will run at a designated time with pre-supplied arguments,
but will also have access to the press config. It is passed in as a keyword argument, even if
unused the function must expect a 'press_config' argument.



Valid hook points are:

* post-press-init
* pre-apply-layout
* pre-mount-fs
* pre-image-ops
* pre-post-config
* pre-create-staging
* pre-target-run
* pre-extensions
* post-extensions


## Example Hook Point

```python

    from press.hooks.hooks import add_hook

    # Hook function must contain argument 'press_config'

    def log_press_config(press_config):
        print(str(press_config))

    add_hook(log_press_config, "post-press-init")

```


