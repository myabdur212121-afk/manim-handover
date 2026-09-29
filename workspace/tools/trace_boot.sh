#!/usr/bin/env bash
# প্রতি টার্নের শুরুতে এক লাইন লেখে, যাতে বোঝা যায় মেশিনটা কখন নতুন করে তৈরি হলো।
L=/home/user/logs/uptime_trace.log
printf '%s  boot=%s  uptime=%dm  manimgl=%s\n' \
  "$(date '+%m-%d %H:%M:%S')" "$(uptime -s)" \
  "$(awk '{print int($1/60)}' /proc/uptime)" \
  "$(command -v manimgl >/dev/null && echo yes || echo GONE)" >> "$L"
tail -8 "$L"
