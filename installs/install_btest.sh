#!/bin/sh

#/***************************************************************************
# * 
# * Copyright (c) 2010 Baidu.com, Inc. All Rights Reserved
# * 
# **************************************************************************/
 
#/**
# * @file install_btest.sh
# * @author wang.dong@baidu.com
# * @date 2010/03/02 18:24:48
# * @version $Revision: 1.7 $ 
# * @brief installation script for btest 
# *  
# **/

##! ********************** configuration **********************

VERSION="1.3.43"
GTEST_TAG="gtest_1-1-1-0_PD_BL"
REPORTLIB_TAG="cpp_2-0-1-1_PD_BL"
MAC_BIT=`/usr/bin/getconf LONG_BIT`
MAC_BIT="${MAC_BIT:-"64"}"
SCM_HOST="ftp://getprod:getprod@product.scm.baidu.com"
BTEST_SITE="ftp://atp.baidu.com/btest${DEBUG_BTEST}/${MAC_BIT}/"
BTEST_FILES="btest-${VERSION}.tar.gz"
VALGRIND_PACKAGE="valgrind-3.5.0.tar.bz2"
PRESENT_DIR=`pwd`
LOG_FILE=${PRESENT_DIR}"/"`date "+%Y_%m_%d_%H_%M_%S"`"_install.log"

BMOCK_PATH="data/prod-64/quality/autotest/bmock/bmock_1-1-4_BL"
FAULT_PATH="data/prod-64/com-test/itest/tools/fault/fault_1-0-3_BL"

LOG_LEVEL=16
#Directory where BTEST will install, (-i dir), $HOME by default
BTEST_DIR=$HOME

#STAT_DATA=`cat $BTEST_DIR/.btest/.bteststat_$(date "+%Y-%m-%d").data 2>/dev/null`
BTEST_WORK_ROOT=$HOME
GTEST_DIR=com/btest/gtest
GTEST_HOME=${BTEST_WORK_ROOT}/com/btest/gtest/output

#For install BTEST in slience
SLIENCE=""

#Install log for used when installing multilple accounts
INSTALL_LOG=~/.install.log

#-f,Èç¹ûsvn workspaceÖÐÏàÓ¦gtestÄ¿Â¼ÒÑ´æÔÚ,y/Y²»ÌáÊ¾,±¸·Ýºó½øÐÐ°²×°;n/NÍË³öbtest°²×°
INSTALL_WITH_BACKUP=""

#-V,Èç¹û±¾µØµÄvalgrind°æ±¾²»·ûÂú×ãÒªÇó,Ôò¿É-VÖ±½ÓÖ¸¶¨°²×°Ä¿Â¼
VALGRIND_INSTALL_DIR=""

#ROLLBACK_LIST=(
#  [0]=0   #~/btest
#  [1]=0   #~/.btest
#  [2]=0   #gtest
#  [3]=0   #reportlib
#  )
ROLLBACK_LIST[0]=0   #$BTEST_DIR/btest
ROLLBACK_LIST[1]=0   #$BTEST_DIR/.btest
ROLLBACK_LIST[2]=0   #gtest
ROLLBACK_LIST[3]=0   #reportlib

CRITICAL=1
ERROR=2
WARNING=4
INFO=8
DEBUG=16

#LOG_LEVEL_TEXT=(
#	[1]="CRITICAL"
#	[2]="ERROR"
#	[4]="WARNING"
#	[8]="INFO"
#	[16]="DEBUG"
#)
LOG_LEVEL_TEXT[1]="CRITICAL"
LOG_LEVEL_TEXT[2]="ERROR"
LOG_LEVEL_TEXT[4]="WARNING"
LOG_LEVEL_TEXT[8]="INFO"
LOG_LEVEL_TEXT[16]="DEBUG"


TTY_FATAL=1
TTY_PASS=2
TTY_TRACE=4
TTY_INFO=8

#TTY_MODE_TEXT=(
#	[1]="[FAIL ]"
#	[2]="[PASS ]"
#	[4]="[TRACE]"
#	[8]="[INFO ]"
#)
TTY_MODE_TEXT[1]="[FAIL ]"
TTY_MODE_TEXT[2]="[PASS ]"
TTY_MODE_TEXT[4]="[TRACE]"
TTY_MODE_TEXT[8]="[INFO ]"

#0  OFF  
#1  ¸ßÁÁÏÔÊ¾
#4  underline  
#5  ÉÁË¸  
#7  ·´°×ÏÔÊ¾
#8  ²»¿É¼û 

#30  40  ºÚÉ«
#31  41  ºìÉ« 
#32  42  ÂÌÉ«  
#33  43  »ÆÉ«  
#34  44  À¶É«
#35  45  ×ÏºìÉ«
#36  46  ÇàÀ¶É«  
#37  47  °×É«

#TTY_MODE_COLOR=(
#	[1]="1;31"	
#	[2]="1;32"
#	[4]="0;36"	
#	[8]="1;33"
#)
TTY_MODE_COLOR[1]="1;31"	
TTY_MODE_COLOR[2]="1;32"
TTY_MODE_COLOR[4]="0;36"	
TTY_MODE_COLOR[8]="1;33"

##! ********************** utils  *********************
Usage()
{
	echo "usage: $0"
	echo "    -d btest_file_dir           Local svn workspace."
	echo "    -i btest_install_dir        Directory where btest will install."
  echo "    -m config_file              Install BTEST for multiple accounts. Format in the config file should follow: account:password@machine"
  echo "    -f                          Force to install btest even if the local workspace directory exists."
  echo "    -s                          Install in slience (no user prompt)"
  echo "    -V [Valgrind Install Dir]   To specify the valgrind install directory."
	echo "    -h                          Get usage."
	exit 0
}

Version()
{
	echo "version = $VERSION"
	exit 0
}

##! @BRIEF: print info to tty
##! @AUTHOR: wang.dong@baidu.com
##! @IN[int]: $1 => tty mode
##! @IN[string]: $2 => message
##! @IN[int]: $3=> go to next row:0=>yes,1=>no
##! @RETURN: 0 => sucess; 1 => fail
Print()
{
	local tty_mode=$1
	local message="$2"
	local goto_next_row=""

	#Èç¹ûµÚ3¸ö²ÎÊýµÄÖµÎª0£¬Ôò²»½øÐÐ»»ÐÐ
	if [ $# -ge 3 ] && [ $3 -eq 0 ]
	then
		goto_next_row="n"
	fi

  echo -e$goto_next_row "\e[${TTY_MODE_COLOR[$tty_mode]}m${TTY_MODE_TEXT[$tty_mode]}${message}\e[m"
	return 0
}

##! @BRIEF: clean env
##! @AUTHOR: wang.dong@baidu.com
##! @RETURN: 0 => success; 1 => failure
CleanEnv()
{
  rm -vf "$PRESENT_DIR/$BTEST_FILES" >> $LOG_FILE 2>&1
  rm -vf "$PRESENT_DIR/$VALGRIND_PACKAGE" >> $LOG_FILE 2>&1
  rm -rvf "$PRESENT_DIR/${BTEST_FILES:0:`expr length $BTEST_FILES`-7}" >> $LOG_FILE 2>&1
  #rm -rvf ${BTEST_WORK_ROOT}/com/btest/output_tmp >> $LOG_FILE 2>&1$
  #cp -rvf ${BTEST_WORK_ROOT}/com/btest/gtest/output ${BTEST_WORK_ROOT}/com/btest/output_tmp >> $LOG_FILE 2>&1$
  #rm -rvf ${BTEST_WORK_ROOT}/com/btest/gtest/* >> $LOG_FILE 2>&1$
  #mv -v ${BTEST_WORK_ROOT}/com/btest/output_tmp ${BTEST_WORK_ROOT}/com/btest/gtest/output >> $LOG_FILE 2>&1$
  #rm -rvf ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp >> $LOG_FILE 2>&1$
  mv "$LOG_FILE" $BTEST_DIR/btest/ >/dev/null 2>&1 
  return 0
}

##! @BRIEF: write log
##! @AUTHOR: xuanbiao@baidu.com
##! @IN[int]: $1 => log level
##! @IN[string]: $2 => message
##! @RETURN: 0 => success; 1 => failure
WriteLog()
{
	local log_level=$1
	local message="$2"

	if [ $log_level -le $LOG_LEVEL ]
	then
		local time=`date "+%Y-%m-%d %H:%M:%S"`
		echo "${LOG_LEVEL_TEXT[$log_level]}: $time: $message" >> $LOG_FILE 2>&1
	  if [ $# -ge 3 ] && [ $3 -eq 0 ]
    then
      return 0
		fi

		case $1 in
			1|2)log_level=1
				;;
			*)	log_level=8
				;;
		esac	
		Print $log_level "$message" 
    echo $log_level "$message" >> ${INSTALL_LOG}
	fi
	return 0
}

##! @BRIEF: send mail
##! @AUTHOR: xuanbiao
##! @IN[string] $1 => mailto
##! @IN[string] $2 => title
##! @IN[string] $3 => content
##! @IN[arr] optional $4 => attachments
##! @RETURN: 0 => sucess; 1 => failure
SendMail()
{
	local mailto="$1"
	local title="$2"
	local content="$3"
	local attach_arr=$4

	local ret
	#×î´óÎÄ¼þ¸öÊý£¬³¬¹ýmax_file_num¸öÔò´ò°ü
	local max_file_num=5
	local gzip_file
	local mail_attach_str
	local attachs=()

	#Èç¹ûÉèÖÃÁË¸½¼þ
	if [ -n "$attach_arr" ]
	then
		attachs=(`eval "echo \"\\\${\$attach_arr[@]}\""`)
		#µ¥¶ÀÒ»¸öÎÄ¼þ¼ÐÖ±½Ó´ò°ü£¬¿¼ÂÇccoverµÄ½á¹û
		if [ ${#attachs[@]} -eq 1 ] && [ -d ${attachs[0]} ]
		then
			gzip_file="${attachs[0]}.tar.gz"
			tar zcf $gzip_file ${attachs[@]}
			mail_attach_str="-a $gzip_file"
		elif [ ${#attachs[@]} -gt $max_file_num ]	#´óÓÚmax_file_numÔò´ò°ü·¢ËÍ
		then
			#FIXME:ÎÄ¼þÃû±ØÐëÊÇÏà¶ÔÂ·¾¶ÇÒ°üº¬Ä¿Â¼Ãû
			local dir=`dirname ${attachs[0]}`
			gzip_file="${dir}.tar.gz"
			tar zcf $gzip_file ${attachs[@]}
			mail_attach_str="-a $gzip_file"
		else
			#for ((i=0; $i<${#attachs[@]}; i=$i+1))
			i=0
      while [ $i -lt ${#attachs[@]} ]
      do
				mail_attach_str="$mail_attach_str -a ${attachs[$i]}"
        ((i++))
			done
		fi
	fi
	#echo "attachs: $mail_attach_str"
	#echo -e "${content}" | mail -s "${title}" "${mailto}"
	#echo -e "<font color='red'>${content}</font>" | mutt -F tmp.muttrc -s "${title}" -a tmp.muttrc "${mailto}"
	#ÉèÖÃÎªÖÐÎÄ±àÂë
	export LANG=zh_CN
	#³­ËÍbtestÓÊ¼þ×é
	echo -e "${content}" | mutt -s "${title}" -c "" ${mail_attach_str} ${mailto} >/dev/null 2>&1
	#echo -e "${content}" | mutt -s "${title}" ${mail_attach_str} ${mailto} >/dev/null 2>&1
	ret=$?
	if [ -n "${gzip_file}" ]
	then
		rm ${gzip_file} >/dev/null 2>&1
	fi
	#echo -e "<font color='red'>${content}</font>" | mutt -s "${title}" -a tmp.muttrc -e "my_hdr Content-Type: text/html" "${mailto}"

	return $ret
}

##! @BRIEF: Install BTEST for multiple accounts
##! @AUTHOR: dongdong@baidu.com
##! @IN[String]: $1 => path of the config file
##! @IN[List]: $2 => parameters of install after -m 
##! @EXIT: 0 => Success; 1 => Failure
InstallMultiAccounts() 
{ 
  local conf_file=$1
  local tool="./util/sl/bin/go"
  local tool_file="util.tar.gz"
  local tool_path="ftp://atp.baidu.com/btest/${tool_file}"
  local install_file="install_btest.sh"
  local install_file_path="ftp://atp/btest${DEBUG_BTEST}/bin/${install_file}"
  #install_file_path="ftp://atp.baidu.com/test/${install_file}"
  local accounts=""
  #Paramters for installing btest on these accounts
  local params="-s"
  INSTALL_LOG=".install.log"
  
  #Check if Valid config file
  if [ -z ${conf_file} ]
  then
    echo "Error! Config file is needed for installing multiple accounts!"
    #Print $TTY_FATAL "Config file is needed for multiple accounts\n" 0
    Usage
  fi
  
  if [ ! -e ${conf_file} ]
  then
    echo "Error! Config file: ${conf_file} does NOT exist!"
    #Print $TTY_FATAL "Config file: ${conf_file} does NOT exist!\n" 0
    exit 1
  fi

  if [ ! -r ${conf_file} ]
  then
    echo "Error! You do NOT have the permission to read the config file: ${conf_file} "
    #Print $TTY_FATAL "You do NOT have the permission to read the config file: ${conf_file}\n" 0
    exit 1
  fi

  #Gather accounts info from config file
  while read -r line
  do
    #echo ${line}
    accounts="${accounts} ${line}"
  done < ${conf_file}
  #echo ${accounts}
  
  #Gather options for install and trim -m option 
  local is_m=""
  for param in $2
  do
    if [ "${is_m}" ]
    then
      is_m=""
      continue
    fi
    if [ ${param} == "-m" ]
     then
       is_m="ture"
       continue
    else
      #echo ${param}
      params="${params} ${param}"
    fi
  done
  #echo ${params}
  
  #Down tools for executing remote command
  wget ${tool_path} 
  tar -xzf ${tool_file}

  #Start to install
  install_command="sh install_btest.sh ${params}"
  if [ "$DEBUG_BTEST" ]
  then
    install_command="export DEBUG_BTEST=_beta; ${install_command}"
  fi
  for account in ${accounts}
  do
    #Downlload install_btest.sh 
    ${tool} ${account} "rm -f install_btest.sh > /dev/null 2>&1"
    #If last statment fails --> account is unreachable
    if [ $? -ne 0 ]
    then
      touch ".$account"
      continue
    fi
    #Download install file
    ${tool} ${account} "wget ${install_file_path}"
    #Init install log
    #${tool} ${account} "echo 8 Install LOG on ${account}: > ${INSTALL_LOG}"
    ${tool} ${account} "rm -f ${INSTALL_LOG} > /dev/null 2>&1"
    #Execute install_btest.sh on this account
    ${tool} ${account} "source ~/.bash_profile; ${install_command}"
    #Clean env on user's account
    ${tool} ${account} "rm -f install_btest.sh > /dev/null 2>&1"
  done
 
  #Display the result to user
  clear
  for account in ${accounts}
  do
    local_log=".install_local.log"
    local log_level
    local message
    Print $TTY_INFO "ÓÃ»§${account}µÄ°²×°ÐÅÏ¢" 1
    #If account is unreachable
    if [ -e ".$account" ]
    then
        echo -e "\e[${TTY_MODE_COLOR[1]}m\nÎÞ·¨Á¬½Óµ½ÓÃ»§ÕË»§£¡ÓÃ»§Ãû¡¢ÃÜÂë»ò»úÆ÷Ãû´íÎó£¬»òÅäÖÃ¸ñÊ½²»·û¡£Çë²é¿´ÅäÖÃÎÄ¼þ!\n\e[m"
        rm -rf ".$account" > /dev/null 2>&1
        continue
    fi
    #Read install log from remote account to a local file
    ${tool} ${account} "cat ${INSTALL_LOG}" > ${local_log}
    #Process the local log file
    while read -r line  
    do
      #echo $line
      log_level=${line%% *}
      message=${line#* }
      #echo $log_level
      if [ "$log_level" = "8" ]
      then
       echo $message
      else
        #Print $CRITICAL "$message\n" 0
        echo -e "\e[${TTY_MODE_COLOR[1]}m${message}\e[m"
      fi
    done < ${local_log}
  done
  
  #clean env
  rm -f ${local_log}
  rm -rf util
  rm -f ${tool_file}
  exit 0
}


##! @BRIEF: process the params 
##! @AUTHOR: xuanbiao@baidu.com
##! @IN[int]: $1 => type:0=>no option;1=>optional;2=>must
##! @IN[string]: $2 => param
##! @IN[string]: $3 => option
##! @OUT[string]: $4 => option value is set if needed
##! @RETURN: n => offset to shift
ProcessParam()
{
	local type=$1
	local param="$2"
	local option="$3"

	#Èç¹ûÃ»ÓÐ»·¾³±äÁ¿
	[ $type -eq 0 ] && return 0

	#´¦Àí²ÎÊý
	case ${option:0:1} in
		-|"")	[ $type -eq 2 ] && echo "option $param requires an argument" && Usage
				return 1
				;;
		*)		eval $4=\"$option\"
				return 2
				;;
	esac

	return 0
}

##! ******************** operation functions **********************

##! @BRIEF: set env variable
##! @AUTHOR: wang.dong@baidu.com
##! @IN[string]: $1 => variable name
##! @IN[string]: $2 => variable value
##! @IN[int]: $3 => single value:0=>true;1=>false
##! @RETURN: 0=>success;1=>fail
SetEnvVar()
{
	local var_name=$1
	local var_value=$2
	local single_value=$3
	local bash_profile_content=`cat ~/.bash_profile`
	local find_btest_flag=0
	local var_add_type=0
	local prefix="export $var_name="
	local prefix_len=`expr length "$prefix"`
	local enter_flag=$'\n'
	local has_btest_flag=`echo "$bash_profile_content" | grep '^#BTEST_FLAG_START$'`

  if [ $# -lt 3 ]
  then
    single_value=0
  fi 
  
	if [ "${var_value:`expr length "$var_value"`-1:1}" == "/" ]
	then
		var_value="${var_value:0:`expr length "$var_value"`-1}"
	fi
	
  #±¸·Ý.bash_profile
  WriteLog $DEBUG "¿ªÊ¼±¸·Ý.bash_profileÎÄ¼þ" 0
  cp "$HOME/.bash_profile" "$HOME/.bash_profile.bak"
	if [ $? -ne 0 ]
	then
		WriteLog $ERROR "±¸·Ý$HOME/.bash_profileÊ§°Ü" 	
        return 1
    fi			

	#Èç¹ûÊÇbtest³õ´ÎÐ´Èë»·¾³±äÁ¿
	WriteLog $INFO "Ð´ÈëBTEST»·¾³±äÁ¿$1..."
	if [ -z "$has_btest_flag" ]
	then
		local warning="###############Please don't modify this section, or errors will occur!###############"
		bash_profile_content="$bash_profile_content$enter_flag$enter_flag$enter_flag$warning$enter_flag#BTEST_FLAG_START$enter_flag"
		if [ $single_value -eq 0 ]
		then
			bash_profile_content="$bash_profile_content$prefix$var_value:$""$var_name$enter_flag"
		else
			bash_profile_content="$bash_profile_content$prefix$var_value$enter_flag"
		fi
		bash_profile_content="$bash_profile_content#BTEST_FLAG_END$enter_flag$warning$enter_flag"
	else
		bash_profile_content=""
      	while read -r oneline
      	do
      		#Èç¹ûÕÒµ½BTEST»·¾³±äÁ¿¿éµÄ¿ªÊ¼±ê¼Ç
      		if [ $find_btest_flag -eq 1 ]
      		then
				#Èç¹ûÓöµ½BTEST»·¾³±äÁ¿¿éµÄ½áÊø±ê¼Ç
				if [ "$oneline" == "#BTEST_FLAG_END" ]
				then
					find_btest_flag=0

					#Èç¹ûÔÚBTEST»·¾³±äÁ¿ÖÐÃ»ÓÐÕÒµ½$1±äÁ¿£¬ÔòÎªÐÂÔö±äÁ¿
					if [ $var_add_type -eq 0 ] 
					then
						if [ $single_value -eq 0 ]
						then
							bash_profile_content="$bash_profile_content$prefix$var_value:$""$var_name$enter_flag"
						else
							bash_profile_content="$bash_profile_content$prefix$var_value$enter_flag"
						fi
					fi
					bash_profile_content="$bash_profile_content$oneline$enter_flag"
					continue
				fi

      			#Èç¹ûÔÚBTEST»·¾³±äÁ¿¿éÖÐÕÒµ½$1»·¾³±äÁ¿
      			if [ "${oneline:0:$prefix_len}" == "$prefix" ]
      			then
      				var_add_type=1
      				bash_profile_content="$bash_profile_content$prefix$var_value"
					
					if [ $single_value -eq 0 ]
					then
						local oneline_len=`expr length "$oneline"`
						local value_list=`echo "${oneline:$prefix_len:$oneline_len-$prefix_len}" | awk -F ':' 'BEGIN{}{for(i=1;i<=NF;i++)print $i;}END{}'`
						for value in $value_list
						do
							if [ ${value:`expr length "$value"`-1:1} ==  "/" ]
							then
								value="${value:0:`expr length "$value"`-1}"
							fi
						
							if [ "$value" != "$var_value" ]
							then
								bash_profile_content="$bash_profile_content:$value"	
							fi
						done
					fi
						bash_profile_content="$bash_profile_content$enter_flag"
      			else
      				bash_profile_content="$bash_profile_content$oneline$enter_flag"
      			fi
				continue
      		fi

      		#ÕÒµ½BTEST»·¾³±äÁ¿¿éµÄ¿ªÊ¼±ê¼Ç
      		if [ "$oneline" == "#BTEST_FLAG_START" ]
      		then
      			find_btest_flag=1
      		fi
      		
      		bash_profile_content="$bash_profile_content$oneline$enter_flag"
      	done < ~/.bash_profile
	fi
	
	WriteLog $DEBUG "½«´¦ÀíºÃºóµÄBTEST»·¾³±äÁ¿Ð´Èëµ½$HOME/.bash_profileÖÐ" 0
	echo -n "$bash_profile_content" > ~/.bash_profile

	return 0
}

##! @BRIEF: °²×°BTEST¸÷²å¼þ
##! @AUTHOR: wang.dong@baidu.com
##! @RETURN: 0=>success;1=>fail
CopyPlugin()
{
	WriteLog $DEBUG "ÇÐ»»¹¤×÷Ä¿Â¼µ½$PRESENT_DIR" 0
	cd "$PRESENT_DIR"
  echo "$PRESNET_DIR"
	if [ $? -ne 0 ]
	then
		WriteLog $CRITICAL "ÎÞ·¨ÇÐ»»Ä¿Â¼µ½$PRESENT_DIR"
		return 1
	fi
	
	WriteLog $INFO "¿ªÊ¼ÏÂÔØBTEST²å¼þµÄ°²×°°ü..."
	wget "$BTEST_SITE$BTEST_FILES" >> $LOG_FILE 2>&1
	if [ $? -eq 0 ]
	then
		WriteLog $INFO "ÏÂÔØBTEST²å¼þ°²×°°ü³É¹¦"
		WriteLog $INFO "¿ªÊ¼½âÑ¹BTEST²å¼þ°²×°°ü..."
		tar -zxvf "$BTEST_FILES" >> $LOG_FILE 2>&1
		if [ $? -eq 0 ]
		then
			WriteLog $INFO "½âÑ¹BTEST²å¼þ°²×°°ü³É¹¦"
			WriteLog $DEBUG "¼ì²â${BTEST_DIR}Ä¿Â¼µÄÐ´ÈëÈ¨ÏÞ..." 0
			if [ ! -w "$BTEST_DIR" ]
			then
				WriteLog $CRITICAL "${BTEST_DIR}Ã»ÓÐÐ´ÈëÈ¨ÏÞ"
        return 1
			fi
			
			local obj_dir="$PRESENT_DIR/${BTEST_FILES:0:`expr length "$BTEST_FILES"`-7}"
			WriteLog $DEBUG "ÇÐ»»µ½Ä¿Â¼${obj_dir}ÖÐ" 0
			cd $obj_dir
			if [ $? -ne 0 ]
			then
				WriteLog $CRITICAL "ÇÐ»»µ½Ä¿Â¼${obj_dir}Ê§°Ü"
				return 1
			fi
						
		  local son_dirs_list=`ls -a`
			for son_dir in $son_dirs_list
			do
				if [ "$son_dir" == "." ] || [ "$son_dir" == ".." ]
				then
          continue
        fi
        if [ "${son_dir}" == ".vim" ]
        then
          cp -brf "${obj_dir}/${son_dir}" "${HOME}"
        else
          rm -rf "${BTEST_DIR}/${son_dir}_old" >> $LOG_FILE 2>&1
          mv "${BTEST_DIR}/${son_dir}" "${BTEST_DIR}/${son_dir}_old" >> $LOG_FILE 2>&1
          mv "${obj_dir}/${son_dir}" "${BTEST_DIR}"
        fi
        if [ $? -ne 0 ]
        then
          WriteLog $CRITICAL "°²×°${son_dir}µ½${BTEST_DIR}Ê§°Ü"
          return 1
        else
          case $son_dir in
            "btest")
              ROLLBACK_LIST[0]=1
              ;;

            ".btest")
              ROLLBACK_LIST[1]=1
              ;;
            
            *)
              ;;
          esac
          WriteLog $INFO "°²×°${son_dir}µ½${BTEST_DIR}³É¹¦"
        fi
			done
		else
			WriteLog $CRITICAL "½âÑ¹BTEST²å¼þ°²×°°üÊ§°Ü"
			return 1
		fi
	else
		WriteLog $CRITICAL "ÏÂÔØBTEST²å¼þ°²×°°üÊ§°Ü"
		return 1
	fi
	
  #Ìí¼ÓÖ´ÐÐbinÄ¿Â¼ÏÂshÎÄ¼þµÄÖ´ÐÐÈ¨ÏÞ
  chmod +x ${BTEST_DIR}/btest/bin/*
	return 0
}

##! @BRIEF: ´ÓSVNÖÐ½«gtest¿âÎÄ¼þcheckout³öÀ´
##! @AUTHOR: wang.dong@baidu.com
##!	@IN[string]: $1 => gtest destination dir
##! @RETURN 0 => success; 1 => fail
CheckoutGtest()
{
  WriteLog $INFO "¼ì²âSVN¹¤¾ßÊÇ·ñ´æÔÚ..."
  svn --version >> $LOG_FILE 2>&1
  if [ $? -ne 0 ]
  then
    WriteLog $CRITICAL "ÄúµÄSVNÃ»ÓÐ°²×°£¬Çë°²×°SVNºóÔÙ³¢ÊÔ"
    return 1
  fi

  WriteLog $INFO "¿ªÊ¼Ç©³öBTest°²×°ÐèÒªµÄÎÄ¼þ"
  BTEST_WORK_ROOT="${BTEST_WORK_ROOT}/"

  #Èç¹û$BTEST_WORK_ROOT$GTEST_DIRÄ¿Â¼´æÔÚ£¬ÔòÌáÊ¾ÊÇ·ñ¼ÌÐø°²×°
  if [ -d "$BTEST_WORK_ROOT$GTEST_DIR" ]
  then
    local choice
    local param_backup=$INSTALL_WITH_BACKUP
    # Èç¹û´¦ÓÚ°²¾²Ä£Ê½£¬Ä¬ÈÏÎª¼ÌÐø°²×°
    if [ $SLIENCE ]
    then
      choice="Y"
    fi
    until [ "$choice" == "Y" ] || [ "$choice" == "y" ] || [ "$choice" == "N" ] || [ "$choice" == "n" ]
    do
      if [ ! -z "$param_backup" ];then
        choice=$param_backup
        param_backup=""
      else
        Print $TTY_INFO "Ä¿Â¼\"$BTEST_WORK_ROOT$GTEST_DIR\"ÒÑ´æÔÚ,¼ÌÐø?(y/n)" 0
        read choice
      fi
    done
    if [ "$choice" == "y" ] || [ "$choice" == "Y" ]
    then
      WriteLog $DEBUG "ÇÐ»»Ä¿Â¼µ½${BTEST_WORK_ROOT}ÖÐ" 0
      cd "${BTEST_WORK_ROOT}"
      if [ $? -ne 0 ]
      then
        WriteLog $CRITICAL "ÎÞ·¨ÇÐ»»Ä¿Â¼µ½${BTEST_WORK_ROOT}"
        return 1
      fi
            
      #±¸·ÝÄ¿Â¼
      if [ -d ${BTEST_WORK_ROOT}/com/btest/gtest ];then
        if [ -d ${BTEST_WORK_ROOT}/com/btest/gtest_old ];then
          rm -rvf ${BTEST_WORK_ROOT}/com/btest/gtest_old >> $LOG_FILE 2>&1
        fi
        mv -v ${BTEST_WORK_ROOT}/com/btest/gtest ${BTEST_WORK_ROOT}/com/btest/gtest_old >> $LOG_FILE 2>&1
        if [ $? -ne 0 ];then
          WriteLog $CRITICAL "±¸·Ý${BTEST_WORK_ROOT}/com/btest/gtestµ½${BTEST_WORK_ROOT}/com/btest/gtest_oldÊ§°Ü"
          return 1
        fi
      fi

      if [ -d ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp ];then
        if [ -d ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp_old ];then
          rm -rvf ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp_old >> $LOG_FILE 2>&1
        fi
        mv -v ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp ${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp_old >> $LOG_FILE 2>&1
        if [ $? -ne 0 ];then
          WriteLog $CRITICAL "±¸·Ý${BTEST_WORK_ROOT}/quality/autotest/reportlib/cppµ½${BTEST_WORK_ROOT}/quality/autotest/reportlib/cpp_oldÊ§°Ü"
          return 1
        fi
      fi
    else
      return 2
    fi
  fi
  
  #Èç¹û¹¤×÷Ä¿Â¼²»´æÔÚ
  if [ ! -d "$BTEST_WORK_ROOT" ];then
    WriteLog $INFO "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}..."
    mkdir -p "$BTEST_WORK_ROOT" >> $LOG_FILE 2>&1
    if [ $? -ne 0 ];then
      WriteLog $CRITICAL "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}Ê§°Ü"
      return 1
    else
      WriteLog $INFO "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}³É¹¦"
    fi
  fi

  #Ç©³ögtest
  #cd "${BTEST_WORK_ROOT}" 2>> $LOG_FILE && cvs co -r $GTEST_TAG com/btest/gtest 2>> $LOG_FILE
  cd "${BTEST_WORK_ROOT}" 2>> $LOG_FILE && svn co https://svn.baidu.com/com/tags/btest/gtest/$GTEST_TAG com/btest/gtest
  if [ $? -ne 0 ];then
    WriteLog $CRITICAL "gtestÇ©³öÊ§°Ü"
    return 1
  else
    ROLLBACK_LIST[2]=1
  fi

  #Ç©³öreportlib
  #cd "${BTEST_WORK_ROOT}" 2>> $LOG_FILE && cvs co -r $REPORTLIB_TAG quality/autotest/reportlib/cpp 2>> $LOG_FILE
  cd "${BTEST_WORK_ROOT}" 2>> $LOG_FILE && svn co https://svn.baidu.com/quality/autotest/tags/reportlib/cpp/$REPORTLIB_TAG quality/autotest/reportlib/cpp
  if [ $? -ne 0 ];then
    WriteLog $CRITICAL "reportlibÇ©³öÊ§°Ü"
    return 1
  else
    ROLLBACK_LIST[3]=1
  fi

  #±àÒëreportlib
  cd "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp 2>> $LOG_FILE && make 2>> $LOG_FILE
  if [ $? -ne 0 ];then
    WriteLog $CRITICAL "reportlib±àÒëÊ§°Ü"
    return 1
  fi
  
  #±àÒëgtest
  cd "${BTEST_WORK_ROOT}"/com/btest/gtest 2>> $LOG_FILE && sh build.sh 2>> $LOG_FILE
  if [ $? -ne 0 ];then
    WriteLog $CRITICAL "gtest±àÒëÊ§°Ü"
    return 1
  fi

  return 0
}

DownloadLib()
{

  BTEST_WORK_ROOT="${BTEST_WORK_ROOT}/"
  BTEST_TMP_DIR=".btest_tmp"

  #Èç¹û$BTEST_WORK_ROOT$GTEST_DIRÄ¿Â¼´æÔÚ£¬ÔòÌáÊ¾ÊÇ·ñ¼ÌÐø°²×°
  LIB_DIR=$1
  LIB_PATH=$2
  if [ -d "$BTEST_WORK_ROOT/$LIB_DIR" ]
  then
    local choice
    local param_backup=$INSTALL_WITH_BACKUP
    # Èç¹û´¦ÓÚ°²¾²Ä£Ê½£¬Ä¬ÈÏÎª¼ÌÐø°²×°
    if [ $SLIENCE ]
    then
      choice="Y"
    fi
    until [ "$choice" == "Y" ] || [ "$choice" == "y" ] || [ "$choice" == "N" ] || [ "$choice" == "n" ]
    do
      if [ ! -z "$param_backup" ];then
        choice=$param_backup
        param_backup=""
      else
        Print $TTY_INFO "Ä¿Â¼\"$BTEST_WORK_ROOT$LIB_DIR\"ÒÑ´æÔÚ,¼ÌÐø?(y/n)" 0
        read choice
      fi
    done
    if [ "$choice" == "y" ] || [ "$choice" == "Y" ]
    then
      WriteLog $DEBUG "ÇÐ»»Ä¿Â¼µ½${BTEST_WORK_ROOT}ÖÐ" 0
      cd "${BTEST_WORK_ROOT}"
      if [ $? -ne 0 ]
      then
        WriteLog $CRITICAL "ÎÞ·¨ÇÐ»»Ä¿Â¼µ½${BTEST_WORK_ROOT}"
        return 1
      fi
            
      #±¸·ÝÄ¿Â¼
      if [ -d ${BTEST_WORK_ROOT}/$LIB_DIR ];then
        if [ -d ${BTEST_WORK_ROOT}/${LIB_DIR}_old ];then
          rm -rvf ${BTEST_WORK_ROOT}/${LIB_DIR}_old >> $LOG_FILE 2>&1
        fi
        mv -v ${BTEST_WORK_ROOT}/${LIB_DIR} ${BTEST_WORK_ROOT}/${LIB_DIR}_old >> $LOG_FILE 2>&1
        if [ $? -ne 0 ];then
          WriteLog $CRITICAL "±¸·Ý${BTEST_WORK_ROOT}/${LIB_DIR}µ½${BTEST_WORK_ROOT}/${LIB_DIR}Ê§°Ü"
          return 1
        fi
      fi
    else
      return 2
    fi
  fi
  
  #Èç¹û¹¤×÷Ä¿Â¼²»´æÔÚ
  if [ ! -d "$BTEST_WORK_ROOT" ];then
    WriteLog $INFO "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}..."
    mkdir -p "$BTEST_WORK_ROOT" >> $LOG_FILE 2>&1
    if [ $? -ne 0 ];then
      WriteLog $CRITICAL "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}Ê§°Ü"
      return 1
    else
      WriteLog $INFO "´´½¨±¾µØSVN¹¤×÷Ä¿Â¼${BTEST_WORK_ROOT}³É¹¦"
    fi
  fi
  
  Print $TTY_INFO "ÏÂÔØ"$LIB_DIR"¿â" 0
  rm -rf ${BTEST_WORK_ROOT}/${BTEST_TMP_DIR}
  mkdir -p ${BTEST_WORK_ROOT}/${BTEST_TMP_DIR}
  #ÏÂÔØ¹¤¾ß¿â
  cd "${BTEST_WORK_ROOT}/${BTEST_TMP_DIR}" 2>> $LOG_FILE && wget -nH -r -l 0 -P ${BTEST_WORK_ROOT}/${BTEST_TMP_DIR} ${SCM_HOST}:/${LIB_PATH} >/dev/null 2>&1
  if [ $? -ne 0 ];then
    WriteLog $CRITICAL "${LIB_DIR}ÏÂÔØÊ§°Ü"
    return 1
  fi
  cd ${BTEST_WORK_ROOT}
  mv ${BTEST_WORK_ROOT}/${BTEST_TMP_DIR}/${LIB_PATH}/output ${BTEST_WORK_ROOT}/${LIB_DIR}
  return 0
}


function get_real_path()
{
    python -c "import os; print os.path.realpath('$1')"
    local ret=$?
    return $ret
}

Init()
{
  if [ $MAC_BIT -eq 32 ]
  then
    WriteLog $INFO "BTestÔÝÊ±²»Ö§³Ö32Î»»úÆ÷!"
    return 2
  fi

	#²ÎÊý´¦Àí²¿·Ö

	#-d¹¤×÷Ä¿Â¼WORK ROOT
	local opt_gtest_core_dir=""
  local btest_install_dir=""
  local config_file_multi=""
  local params="$@"

  
	#¿ªÊ¼Ñ­»·´¦Àí²ÎÊý
	while [ $# -gt 0 ]
	do
		case "$1" in
			-v) Version
				shift
				;;
			-h) Usage
				shift
				;;
			#-d ¹¤×÷Ä¿Â¼£¬Ä¬ÈÏÎª$HOME
			-d)	ProcessParam 1 "$1" "$2" opt_gtest_core_dir
				shift $?
				;;
			#-i BTEST°²×°Ä¿Â¼£¬Ä¬ÈÏÎª$HOME
			-i)	ProcessParam 2 "$1" "$2" btest_install_dir
				shift $?
        ;;
      #-m Îª¶à¸öÓÃ»§°²×°BTEST
      -m) ProcessParam 2 "$1" "$2" config_file_multi
        InstallMultiAccounts "$config_file_multi" "${params}"
        shift $?
        ;;
			#-f Èç¹ûsvn workspace dirÖÐÏàÓ¦gtestÄ¿Â¼ÒÑ´æÔÚ,Ñ¡Ôñ±¸·Ý°²×°»òÍË³ö°²×°
			-f)	ProcessParam 1 "$1" "$2" INSTALL_WITH_BACKUP 
				shift $?
				;;
      #-s ½ûÖ¹ÓÃ»§ÌáÊ¾£¨forÔ¶³Ì°²×°£©
      -s) SLIENCE="true"
        shift
        ;;
			#-V Ö±½ÓÖ¸¶¨°²×°Ä¿Â¼
			-V)	ProcessParam 1 "$1" "$2" VALGRIND_INSTALL_DIR
				shift $?
				;;
			*)  echo "Unkown option \"$1\""
				Usage
				;;
		esac
	done

  # Èç¹ûÓÃ»§×Ô¼ºÖ¸¶¨°²×°Ä¿Â¼
  if [ $btest_install_dir ]
  then
    # ÐèÒªÊ¹ÓÃ¾ø¶ÔÂ·¾¶
    if [ "${btest_install_dir:0:1}" != "/" ]
    then
      echo "ÇëÊäÈëBTESTµÄ°²×°Ä¿Â¼µÄ¾ø¶ÔÂ·¾¶£¡"
      Usage
    fi
    BTEST_DIR="`dirname $btest_install_dir`/`basename $btest_install_dir`"
    # Èç¹ûÓÃ»§Ö¸¶¨Ä¿Â¼²»´æÔÚ
    if [ ! -d "${BTEST_DIR}" ]
    then
      mkdir -p "${BTEST_DIR}"
    fi
    WriteLog $INFO "ÄúÉèÖÃµÄBTEST°²×°Ä¿Â¼Îª${BTEST_DIR}"
  fi
  
  
	#Èç¹ûWORK ROOTÎª¿Õ
	if [ -z $opt_gtest_core_dir ]
	then
    #Èç¹û²»ÊÇ°²¾²Ä£Ê½,ÌáÊ¾ÓÃ»§Ö¸¶¨SVN¹¤×÷Ä¿Â¼
    if [ -z $SLIENCE ]
    then
      local choice
      local ret=1
      while [ $ret -ne 0 ]
      do
        Print $TTY_INFO "ÄúÃ»ÓÐÖ¸¶¨±¾µØSVN¹¤×÷Ä¿Â¼£¬ÏÖÔÚÊ¹ÓÃ¾ø¶ÔÂ·¾¶½øÐÐÖ¸¶¨?(y/n)" 0
        read -n 1 choice
        echo "${choice}" | grep -iE "(y|n)" &>/dev/null
        ret=$?
        echo ""
        [ $ret -eq 0 ] && break
      done
      if [ "$choice" == "Y" ] || [ "$choice" == "y" ]
      then
        #WORK_ROOT±ØÐëÎªÒ»¸ö¾ø¶ÔÂ·¾¶
        until [ "${opt_gtest_core_dir:0:1}" == "/" ]
        do 
          Print $TTY_INFO "ÇëÊäÈëÄú±¾µØSVN¹¤×÷Ä¿Â¼µÄ¾ø¶ÔÂ·¾¶:" 0
          read opt_gtest_core_dir
          local btest_dir_len=`expr length "$BTEST_DIR/btest"`
          local workspace_real_path="`get_real_path \"${opt_gtest_core_dir}\"`"
          if [ "$BTEST_DIR/btest" == "${workspace_real_path:0:$btest_dir_len}" ]
          then
            Print $TTY_INFO "×¢Òâ:ÊäÈëµÄÂ·¾¶²»ÄÜÊÇ${BTEST_DIR}/btestÄ¿Â¼¼°Æä×ÓÄ¿Â¼"
            opt_gtest_core_dir=""
          fi
        done
      else
        opt_gtest_core_dir=$HOME
      fi
    #Èç¹ûÎª°²¾²Ä£Ê½
    else
        opt_gtest_core_dir=$HOME
    fi 
  else
    if [ "${opt_gtest_core_dir:0:1}" != "/" ]
    then
      WriteLog $INFO "Ö¸¶¨µÄ±¾µØSVN¹¤×÷Ä¿Â¼±ØÐëÎª¾ø¶ÔÂ·¾¶"
      return 1
    fi
	fi
  WriteLog $INFO "ÄúÉèÖÃµÄ±¾µØSVN¹¤×÷Ä¿Â¼Îª${opt_gtest_core_dir}"
 
  BTEST_WORK_ROOT="`dirname $opt_gtest_core_dir`/`basename $opt_gtest_core_dir`"
  GTEST_HOME="${BTEST_WORK_ROOT}/${GTEST_DIR}"/output
  
  #´Ósvn¿âÖÐcheckout³ögtest
  CheckoutGtest
  case $? in
    1)return 1
      ;;
    2)return 2
      ;;
    *)
      DownloadLib fault ${FAULT_PATH} 
      if [ $? -ne 0 ]
      then
          return 1
      fi
      DownloadLib bmock ${BMOCK_PATH} 
      if [ $? -ne 0 ]
      then
          return 1
      fi
      CopyPlugin
      if [ $? -ne 0 ]
      then
        return 1
      fi

      ## Add by yangzunhao@baidu.com, 2012-4-10
      ## ´Ótool.baidu.comÉÏwget install_errHunter.sh½Å±¾µ½µ±Ç°Ä¿Â¼²¢ÔËÐÐ´Ë½Å±¾°²×°errHunter
      ## °²×°Íê±ÏºóÉ¾³ý´ËÁÙÊ±½Å±¾       
      #local errHunter_install_shell_url=http://tool.baidu.com/p/errHunter/downloadFile/87
      local errHunter_install_shell_url=http://tool.baidu.com/p/errHunter/downloadFileByName/install_errHunter.sh
      wget $errHunter_install_shell_url -O install_errHunter.sh 2>/dev/null
      if [ -s "/dev/null" ]
      then
        WriteLog $ERROR "errHunter  °²×°Ê§°Ü£¡" 0
      fi
      chmod u+x ./install_errHunter.sh
      ./install_errHunter.sh -i $BTEST_DIR/btest
      rm -f ./install_errHunter.sh

      #½«BTESTÖÐµÄ»·¾³±äÁ¿$WORK_ROOT,$BTEST_HOME,$GTEST_HOME,$LD_LIBRARY_PATHÐ´Èë½.bash_profileÖÐ
      WriteLog $INFO "¿ªÊ¼ÉèÖÃ»·¾³±äÁ¿..."
      SetEnvVar "BTEST_WORK_ROOT" "$BTEST_WORK_ROOT" 1
      SetEnvVar "BTEST_HOME" "$BTEST_DIR/btest" 1
      SetEnvVar "GTEST_HOME" "$GTEST_HOME" 1
      SetEnvVar "LD_LIBRARY_PATH" '$GTEST_HOME/lib'
      SetEnvVar "PATH" '$BTEST_HOME/bin'
      
      WriteLog $INFO "¼ì²âvalgrind..."
      local valgrind_is_ok=1
      local version
      version=`valgrind --version 2>/dev/null`
      if [ $? -ne 0 ]
      then
        valgrind_is_ok=0
        WriteLog $ERROR "valgrindÃ»ÓÐ°²×°£¬½«ÎÞ·¨Ê¹ÓÃBTESTµÄvalgrind¼ì²â¹¦ÄÜ!" 0
      else
        file_valgrind="$(file -L $(which valgrind))" 
        tool_bit=`echo $file_valgrind | grep "ELF ${MAC_BIT}-bit LSB executable"`
        if [ -z "$tool_bit" ]
        then
          valgrind_is_ok=0
          WriteLog $ERROR "Äú°²×°µÄvalgrindÓë»úÆ÷µÄÎ»Êý²»·û£¬½«ÎÞ·¨Ê¹ÓÃBTESTµÄvalgrind¼ì²â¹¦ÄÜ" 0
        else
          if [[ $version < "valgrind-3.4.0" ]]
          then
            valgrind_is_ok=0
            WriteLog $ERROR "Äú°²×°µÄvalgrind°æ±¾Ì«µÍ,½¨ÒéÊ¹ÓÃvalgrind-3.4.0(º¬)ÒÔÉÏ£¬½«ÎÞ·¨Ê¹ÓÃBTESTµÄvalgrind¼ì²â¹¦ÄÜ" 0
          fi
        fi
      fi

      if [ ${valgrind_is_ok} -eq 0 ]
      then
        choice=""
        #Èç¹ûÎª°²¾²Ä£Ê½£¬Ä¬ÈÏÎª°²×°, Ä¬ÈÏ°²×°Ä¿Â¼Îª$HOME
        if [ $SLIENCE ]
        then
          VALGRIND_INSTALL_DIR=$HOME
          choice="Y"
        fi
        until [ "$choice" == "Y" ] || [ "$choice" == "y" ] || [ "$choice" == "N" ] || [ "$choice" == "n" ]
        do
          if [ ! -z "$VALGRIND_INSTALL_DIR" ];then
            choice="y"
          else
            Print $TTY_INFO "Ã»ÓÐ¼ì²âµ½ÊÊºÏbtestµÄvalgrind°æ±¾£¬ÊÇ·ñ°²×°ºÏÊÊµÄvalgrind?(y/n)" 0
            read choice
          fi
        done

        if [ "$choice" == "Y" ] || [ "$choice" == "y" ]
        then
          WriteLog $INFO "¿ªÊ¼ÏÂÔØvargrind°²×°ÎÄ¼þ..." 
          cd "$PRESENT_DIR" && wget "$BTEST_SITE$VALGRIND_PACKAGE" >> $LOG_FILE 2>&1
          if [ $? -ne 0 ]
          then
            WriteLog $ERROR "ÏÂÔØvalgrind°²×°ÎÄ¼þÊ§°Ü"  
          else
            WriteLog $INFO "ÏÂÔØvalgrind°²×°ÎÄ¼þ³É¹¦"  
            local param_valgrind_install_dir=$VALGRIND_INSTALL_DIR
            while true
            do
              local valgrind_install_dir=""
              while true
              do 
                if [ ! -z "$param_valgrind_install_dir" ];then
                  valgrind_install_dir=$param_valgrind_install_dir
                  param_valgrind_install_dir=""
                else
                  Print $TTY_INFO "ÇëÊäÈëÓÐÐ´ÈëÈ¨ÏÞµÄvalgrind°²×°Ä¿Â¼µÄ¾ø¶ÔÂ·¾¶: " 0
                  read valgrind_install_dir
                fi
                [ "${valgrind_install_dir:0:1}" == "/" ] && break
              done

              if [ ! -d "${valgrind_install_dir}" ]
              then
                mkdir -p "${valgrind_install_dir}" >> $LOG_FILE 2>&1
                if [ $? -ne 0 ]
                then
                  WriteLog $ERROR "´´½¨valgrind°²×°Ä¿Â¼${valgrind_install_dir}Ê§°Ü"
                else
                  WriteLog $INFO "´´½¨valgrind°²×°Ä¿Â¼${valgrind_install_dir}³É¹¦"
                fi
              fi

              if [ -w "${valgrind_install_dir}" ]
              then
                break
              else
                [ -d "${valgrind_install_dir}" ] && WriteLog $ERROR "ÄúÊäÈëµÄvalgrind°²×°Ä¿Â¼Ã»ÓÐÐ´ÈëÈ¨ÏÞ!"
              fi
            done

            WriteLog $INFO "¿ªÊ¼°²×°valgrind¹¤¾ß,ÇëÄÍÐÄµÈ´ý..."
            cd "$PRESENT_DIR" && tar -jxvf "$VALGRIND_PACKAGE" && cd valgrind-3.5.0 && ./configure --prefix="${valgrind_install_dir}" && make && make install >> $LOG_FILE 2>&1
            if [ $? -ne 0 ]
            then
              WriteLog $ERROR "°²×°valgrindÊ§°Ü"
            else
              WriteLog $INFO "Ð´ÈëvalgrindµÄ»·¾³±äÁ¿" 0
              if [ "$HOME" == "${valgrind_install_dir}" ]
              then
                SetEnvVar "PATH" '$HOME/bin'
              else
                SetEnvVar "PATH" "${valgrind_install_dir}/bin" 
              fi
              WriteLog $INFO "°²×°valgrind³É¹¦"
            fi
            cd .. && rm -rvf "$PRESENT_DIR"/valgrind-3.5.0 "$PRESENT_DIR/$VALGRIND_PACKAGE" >> $LOG_FILE 2>&1
          fi
        else
          WriteLog $ERROR "Äú½«ÎÞ·¨Ê¹ÓÃBTESTµÄvalgrind¼ì²â¹¦ÄÜ"
        fi
      fi
      
      WriteLog $INFO "¼ì²âccoverÊÇ·ñ´æÔÚ..."
      which covc >/dev/null 2>&1
      if [ $? -ne 0 ]
      then
        WriteLog $ERROR "ccoverÃ»ÓÐ°²×°£¬½«ÎÞ·¨Ê¹ÓÃBTESTµÄ´úÂë¸²¸ÇÂÊ·ÖÎö¹¦ÄÜ"
      fi

      WriteLog $INFO "Æô¶¯×Ô¶¯¸üÐÂ..." 0
      local btest_crontab="/tmp/btest_crontab_"`whoami`
      local btest_crontab_new="${btest_crontab}_new"
      crontab -l > $btest_crontab
      echo "00 01 * * * source $HOME/.bash_profile;$BTEST_DIR/btest/bin/update_btest" >> $btest_crontab
      crontab -r >/dev/null 2>&1
      echo -n > "${btest_crontab_new}"
      while read -r line
      do
        #È¥³ý¾É°æ±¾ÖÐµÄÃüÁî
        if [ "$line" == "00 13 * * * python $BTEST_DIR/btest/bin/update_btest.py" ]
        then
          continue
        fi

        #È¥³ýÖØ¸´µÄÃüÁî
        local exist_rec=0
        while read -r newline
        do
          if [ "$newline" == "$line" ]
          then
            exist_rec=1
            break
          fi
        done < ${btest_crontab_new}

        if [ $exist_rec -eq 0 ]
        then
          echo "$line" >> "${btest_crontab_new}"
        fi
      done < $btest_crontab
      crontab $btest_crontab_new >> $LOG_FILE 2>&1
      if [ $? -ne 0 ]
      then
        WriteLog $ERROR "Æô¶¯×Ô¶¯¸üÐÂÊ§°Ü"
      fi
      rm -rvf $btest_crontab_new >>$LOG_FILE 2>&1

      WriteLog $INFO "BTEST-${VERSION}°²×°³É¹¦"
      local banner="ÇëÊ¹ÓÃÒÔÏÂÃüÁîÊ¹BTEST°²×°ÉúÐ§:"
      local tips="source ~/.bash_profile"
      WriteLog $INFO "$tips" 0
      echo -e$goto_next_row "\033[32;49;5m${TTY_MODE_TEXT[8]}${banner}\033[39;49;0m"
      echo -e$goto_next_row "\033[32;49;1m${TTY_MODE_TEXT[8]}${tips}\033[39;49;0m"
      ;;
  esac

  STAT_DATA=`cat $BTEST_DIR/.btest/.bteststat_$(date "+%Y-%m-%d").data 2>/dev/null`
  
  [ ! -z "${STAT_DATA}" ] && echo "${STAT_DATA}" >> $BTEST_DIR/.btest/.bteststat_$(date "+%Y-%m-%d").data
  echo "utils#installationtimes#"$(date "+%Y-%m-%d %H:%M:%S") >> $BTEST_DIR/.btest/.bteststat_$(date "+%Y-%m-%d").data
  return 0
}

InitCallback()
{
    local ret=$1
    case $ret in
      0)
        #°²×°³É¹¦,É¾³ý±¸·ÝÎÄ¼þ
        #[ -d "$BTEST_DIR/btest_btestbak" ] && rm -rvf ~/btest_btestbak >> $LOG_FILE 2>&1
        #[ -d "$BTEST_DIR/.btest_btestbak" ] && rm -rvf ~/.btest_btestbak >> $LOG_FILE 2>&1
        #[ -d "${GTEST_HOME}_btestbak" ] && rm -rvf ${GTEST_HOME}_btestbak >> $LOG_FILE 2>&1

        #°²×°³É¹¦ºóÁ¢¼´Ö´ÐÐÒ»´Î¸üÐÂ
        WriteLog $INFO "BTESTÕýÔÚÉý¼¶ÖÐ£¬´óÔ¼Ðè3-5·ÖÖÓ£¬Çë²»ÒªÊ¹ÓÃCtrl+CÇ¿ÐÐÖÕÖ¹!"
        result=`source ~/.bash_profile;~/btest/bin/update_btest >/dev/null 2>&1`
        if [ $? -ne 0 ]
        then
          echo "$result" >> $LOG_FILE
        fi
        ;;

      1)
        #°²×°Ê§°Ü,»Ø¹öÄ¿Â¼
        length=${#ROLLBACK_LIST[@]}
        #for ((i=0; $i<$length; i++))
        i=0
        while [ $i -lt $length ]
        do
          if [ ${ROLLBACK_LIST[$i]} -eq 1 ]
          then
            case $i in
              0)
                [ -d "$BTEST_DIR/btest" ] && rm -rvf $BTEST_DIR/btest >> $LOG_FILE 2>&1
                [ -d "$BTEST_DIR/btest_old" ] && mv -v $BTEST_DIR/btest_old $BTEST_DIR/btest >> $LOG_FILE 2>&1
                ;;

              1)
                [ -d "$BTEST_DIR/.btest" ] && rm -rvf $BTEST_DIR/.btest >> $LOG_FILE 2>&1
                [ -d "$BTEST_DIR/.btest_old" ] && mv -v $BTEST_DIR/.btest_old $BTEST_DIR/.btest>> $LOG_FILE 2>&1
                ;;

              2)
                [ -d "${BTEST_WORK_ROOT}/${GTEST_DIR}" ] && rm -rvf "${BTEST_WORK_ROOT}/${GTEST_DIR}" >> $LOG_FILE 2>&1
                [ -d "${BTEST_WORK_ROOT}/${GTEST_DIR}"_old ] && mv -v "${BTEST_WORK_ROOT}/${GTEST_DIR}"_old "${BTEST_WORK_ROOT}/${GTEST_DIR}" >> $LOG_FILE 2>&1
                ;;

              3)
                [ -d "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp ] && rm -rvf "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp >> $LOG_FILE 2>&1
                [ -d "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp_old ] && mv -v "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp_old "${BTEST_WORK_ROOT}"/quality/autotest/reportlib/cpp >> $LOG_FILE 2>&1
                ;;

              *)
                ;;
            esac
          fi
          ((i++))
        done
        
        attach[0]="$LOG_FILE"
        
        #SendMail "btest-mon@baidu.com" "[BTest]°²×°Ê§°Ü" "" attach
        ;;

      *)
        ;;
    esac

    WriteLog $INFO "ÈçÓÐÎÊÌâ£¬ÇëÁªÏµbtest@baidu.com,Ð»Ð»!"

    #ÇåÀí»·¾³
    CleanEnv
}

Main()
{
    Init "$@"
    InitCallback $?
}

Main "$@"
