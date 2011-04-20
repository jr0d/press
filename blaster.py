from parted import PartedInterface, PartedInterfaceException, PartedException
from types import Layout, Partition, Size

class BlasterMaster(object):
    '''
    This class will take a Layout object and provide a clean interface to 
    blast the changes on the disk. The default behavior of the class will 
    be to remove the current partitiion table, write the new partition table,
    and create the file systems as represented by the Layout object. 

    This class will also blast any data you want onto the file systems it 
    created, using a pluggin interface. Support for rsync and a next generation
    image format will be provided by default, if you are using the standard 
    press packages.
                                                                             
        __/__/      __/           __/       __/__/ __/__/__/ __/__/ __/__/   
       __/  __/    __/         __/ __/     __/       __/    __/    __/  __/  
      __/   __/   __/        __/    __/   __/       __/    __/    __/   __/  
     __/__/__/   __/       __/__/__/__/  __/__/    __/    __/__/ __/__/__/   
    __/    __/  __/       __/       __/    __/    __/    __/    __/    __/   
   __/    __/  __/       __/       __/    __/    __/    __/    __/    __/    
  __/__/__/   __/__/__/ __/       __/ __/__/    __/    __/__/ __/    __/     
                                                                             
         __/__/    __/__/     __/       __/__/ __/__/__/ __/__/ __/__/       
        __/ __/  __/ __/   __/ __/     __/       __/    __/    __/  __/      
       __/  __/__/  __/  __/    __/   __/       __/    __/    __/   __/      
      __/    __/   __/ __/__/__/__/  __/__/    __/    __/__/ __/__/__/       
     __/          __/ __/       __/    __/    __/    __/    __/    __/       
    __/          __/ __/       __/    __/    __/    __/    __/    __/        
   __/          __/ __/       __/ __/__/    __/    __/__/ __/    __/         


    '''

