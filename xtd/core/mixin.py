# -*- coding: utf-8
#------------------------------------------------------------------#

__author__    = "Xavier MARCELET <xavier@marcelet.com>"

#------------------------------------------------------------------#

class Singleton(type):
  m_instances = {}
  def __call__(p_class, *p_args, **p_kwargs):
    if p_class not in p_class.m_instances:
      p_class.m_instances[p_class] = super(Singleton, p_class).__call__(*p_args, **p_kwargs)
    return p_class.m_instances[p_class]


#------------------------------------------------------------------#

