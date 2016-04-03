#!/usr/bin/env python3
#------------------------------------------------------------------#

__author__    = "Xavier MARCELET <xavier@marcelet.com>"

#------------------------------------------------------------------#

import json
import os
import sys
import requests
import argparse
import subprocess

l_path = os.path.realpath(os.path.dirname(__file__))
os.chdir(os.path.dirname(l_path))
sys.path.append(".")

#------------------------------------------------------------------#

# l_path=$(readlink -f $0)
# cd $(dirname $(dirname ${l_path}))


# l_token=$1; shift
# l_buildID=$1; shift
# l_commit=$1; shift

# if [ -z "${l_commit}" ]; then
#   l_commit=$(git rev-parse HEAD)
# fi

class StatusHelper:
  def __init__(self):
    self.m_dryrun = False
    self.m_parser = argparse.ArgumentParser("xtd build checker")
    self.m_parser.add_argument("--token",    help="Github API secret token", dest="m_token",   required=True)
    self.m_parser.add_argument("--build-id", help="Travis build-id",         dest="m_buildID", required=True)
    self.m_parser.add_argument("--commit",   help="Current git commit hash", dest="m_commit",  required=True)
    self.m_parser.add_argument("--dry-run",  help="Do not push statuses to github", dest="m_dryrun", action="store_true")
    self.m_parser.parse_args(sys.argv[1:], self)

  def getTargetUrl(self):
    l_url = "https://travis-ci.org/psycofdj/xtd/builds/%(buildID)s"
    return l_url % {
      "buildID" : self.m_buildID
    }

  def send_status(self, p_status, p_tag, p_description):
    if self.m_dryrun:
      return {}

    l_url    = "https://api.github.com/repos/%(user)s/%(repo)s/statuses/%(commit)s" % {
      "user"   : "psycofdj",
      "repo"   : "xtd",
      "commit" : self.m_commit
    }
    l_params  = { "access_token" : self.m_token }
    l_headers = { "Content-Type" : "application/json" }
    l_data    = {
      "state"       : p_status,
      "target_url"  : self.getTargetUrl(),
      "description" : p_description,
      "context"     : p_tag
    }

    l_req = requests.post(l_url, params=l_params, headers=l_headers, data=json.dumps(l_data))
    return l_req.json()


  def run_unittests(self):
    print("-------------------")
    print("Running test suites")
    print("-------------------")

    l_proc = subprocess.Popen(["python3", "./devtools/unittests.py", "--format", "json", "-v"], stdout=subprocess.PIPE)
    l_proc.wait()
    try:
      l_lines = l_proc.stdout.read().decode("utf-8")
      l_data = json.loads(l_lines)
      l_info = {
        "nbtests" : l_data["tests"],
        "nbok"    : l_data["success"],
        "nbko"    : l_data["tests"] - l_data["success"]
      }
      l_description = "Ran %(nbtests)d tests : %(nbok)d success, %(nbko)d errors" % l_info
      l_status = "error"
      if l_info["nbko"] == 0:
        l_status = "success"
      for c_test in l_data["details"]["success"]:
        print("oK : %(file)s:%(class)s:%(method)s" % c_test)
      for c_test in l_data["details"]["errors"]:
        print("Ko : %(file)s:%(class)s:%(method)s : %(message)s" % c_test)
      for c_test in l_data["details"]["failures"]:
        print("Ko : %(file)s:%(class)s:%(method)s : %(message)s" % c_test)
      for c_test in l_data["details"]["expectedFailures"]:
        print("Ko : %(file)s:%(class)s:%(method)s : %(message)s" % c_test)
      for c_test in l_data["details"]["unexpectedSuccesses"]:
        print("Ko : %(file)s:%(class)s:%(method)s" % c_test)
      print("")
      print("Ran %(nbtests)d tests, %(nbok)d success, %(nbko)d failures" % l_info)
    except Exception as l_error:
      l_status      = "failure"
      l_description = "unexpected error while reading unittests results"
      print("error while running unittests : %s" % (l_error))
    self.send_status(l_status, "checks/unittests", l_description)
    print("")

  def run_pylint(self):
    print("-------------------")
    print("Running pylint     ")
    print("-------------------")

    l_proc = subprocess.Popen(["python3", "./devtools/xtdlint.py", "--rcfile", ".pylintrc", "-j", "4", "xtd" ], stdout=subprocess.PIPE)
    l_proc.wait()
    try:
      l_lines      = l_proc.stdout.read().decode("utf-8")
      l_data       = json.loads(l_lines)
      l_score      = l_data["report"]["score"]
      l_nbErrors   = l_data["report"]["errors"]["by_cat"].get("fatal", 0)
      l_nbErrors  += l_data["report"]["errors"]["by_cat"].get("error", 0)

      if l_score < 9:
        l_status = "error"
        l_description = "pylint score %.2f/10 too low" % l_score
      elif l_nbErrors != 0:
        l_status = "error"
        l_description = "pylint detected '%d' unacceptables errors" % l_nbErrors
      else:
        l_status = "success"
        l_description = "pylint score is %.2f/10" % l_score
      for c_module, c_data in l_data["errors"].items():
        for c_msg in c_data["items"]:
          c_msg["path"] = c_data["path"]
          print("%(C)s:%(symbol)-20s %(path)s:%(line)d:%(column)d " % c_msg)
      print("")
      print("Final score : %.2f/10" % l_score)
    except Exception as l_error:
      l_status      = "failure"
      l_description = "unexpected error while reading pylint results"
      print("error while running pylint : %s" % (l_error))
    self.send_status(l_status, "checks/pylint", l_description)
    print("")

  def run_sphinx(self):
    print("------------------------")
    print("Genrating documentation ")
    print("------------------------")

    l_proc = subprocess.Popen(["sphinx-build", "-qaNW", "-b", "html", "-d", "../build/docs/cache", ".", "../build/docs/html" ], cwd="./docs", stderr=subprocess.PIPE)
    l_proc.wait()
    if l_proc.returncode != 0:
      l_status      = "error"
      l_description = "error while generating documentation"
    else:
      l_status      = "success"
      l_description = "documentation successfully generated"

    l_lines = l_proc.stderr.readlines()
    if len(l_lines):
      for c_line in l_lines:
        print(c_line.decode("utf-8"))
    else:
      print("")
      print("Documentation OK")
    self.send_status(l_status, "checks/documentation", l_description)
    print("")


  def run(self):
    self.send_status("pending", "checks/unittests",     "running unittests...")
    self.send_status("pending", "checks/pylint",        "running pylint...")
    self.send_status("pending", "checks/documentation", "running sphinx...")
    self.run_unittests()
    self.run_pylint()
    self.run_sphinx()

if __name__ == "__main__":
  l_app = StatusHelper()
  l_app.run()