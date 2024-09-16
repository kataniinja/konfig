# Практическое занятие №1. Введение, основы работы в командной строке

Ерченков А. А. - ИКБО-62-23

## Задание 1

```
grep '^[^:]*' /etc/passwd | cut -d: -f1 | sort
```
![image](https://github.com/user-attachments/assets/42ab2124-e9b1-4faa-956b-b29e3559d06d)

## Задание 2

```
cat /etc/protocols | awk '{print $2, $1}' | sort -nr | head -n 5
```
![image](https://github.com/user-attachments/assets/61e1654c-345b-41c8-99a3-e393d30d913c)

## Задание 3

```
#!/bin/bash
if [ "$#" -ne 1 ];  then
        echo "Использование: $0 \"Ваш текст\""
        exit -1
fi

text="$1"
length=${#text}

frame_length=$((length + 2))

printf '+%s+\n' "$(printf '%*s' "$frame_length" '' | tr ' ' '-')"
printf '| %s |\n' "$text"
printf '+%s+\n' "$(printf '%*s' "$frame_length" '' | tr ' ' '-')"
```
![image](https://github.com/user-attachments/assets/ae857ba1-ea52-4f28-96bd-12418431e8f0)

## Задание 4

```
#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Используйте: $0 имя_файла"
	exit 1
fi

file="$1"

grep -oE '\b[a-zA-Z_][a-zA-Z0-9_]*\b' "$file" | sort -u
```
![image](https://github.com/user-attachments/assets/cd0f72ea-83cd-4c41-8ee5-ec8d3a8ecda9)

## Задание 5

```
#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Используйте: $0 имя команды."
	exit 1
fi

command_name="$1"
command_path="./$command_name"

if [ ! -f "$command_path" ]; then
	echo "Ошибка: файл '$command_path' не найден."
	exit 1
fi

sudo chmod +x "$command_name"
sudo cp "$command_path" /usr/local/bin/

if [ $? -ne 0 ]; then
	echo "Ошибка: не удалось скопировать файл."
	exit 1
fi

sudo chmod 775 /usr/local/bin/"$command_name"

if [ $? -ne 0 ]; then
	echo "Ошибка: не удалось установить права для '$command_name'."
	exit 1
fi

echo "Команда '$command_name' успешно зарегестрирована."
```
![image](https://github.com/user-attachments/assets/5a08fa01-3a6b-4744-adac-38e407b88a04)

## Задание 6

```
#!/bin/bash

check_comment() {
	local file=$1
	local ext=${file##*.}

	echo "Проверка: $file с расширением: .$ext"
	
	case $ext in
		c)
			if head -n 1 "$file" | grep -q '^\s*//' || head -n 1 "$file" | grep -q '^\s*/\*'; then
				echo "$file: Есть комментарий."
			else
				echo "$file: Нет комментария."
			fi
			;;
		js)
			if head -n 1 "$file" | grep -q '^\s*//'; then
				echo "$file: Есть комментарий."
			else
				echo "$file: Нет комментария."
			fi
			;;
		py)
			if head -n 1 "$file" | grep -q '^\s*#'; then
				echo "$file: Есть комментарий."
			else
				echo "$file: Нет комментария."
			fi
			;;
		*)
			echo "$file: Неподдерживаемый формат."
			;;
	esac
}


if [[ $# -ne 1 ]]; then
	echo "Использование: $0 <имя_файла>."
	exit 1
fi

if [[ -f $1 ]]; then
	check_comment "$1"
else
	echo "Файл $file не найден."
	exit 1
fi
```
![image](https://github.com/user-attachments/assets/2b9b0384-c7c8-41b1-91fa-c8fb359c0b3b)

## Задание 7

```
#!/bin/bash

if [[ $# -ne 1 ]]; then
	echo "Использование: $0 /путь/к/каталогу."
	exit 1
fi

directory=$1

if [[ ! -d $directory ]]; then
	echo "Ошибка: каталог $directory не найден."
	exit 1
fi

declare -A file_hashes

while IFS= read -r -d '' file; do
	hash=$(sha256sum "$file" | awk '{ print $1 }')
	file_hashes["$hash"]+="file"$'\n'
done < <(find "$directory" -type f -print0)

found_duplicates=false

for hash in "${!file_hashes[@]}"; do
	files="${file_hashes[$hash]}"
	files_count=$(echo -e "files" | wc -l)


	if [[ $files_count -gt 1 ]]; then
		found_duplicates=true
		echo "Найдены дубликаты:"
		echo -e "$files"
	fi
done

if ! $found_duplicates; then
	echo "Дубликатов не найдено."
	exit 1
fi
```
![image](https://github.com/user-attachments/assets/b4fd6d45-67b8-472e-bf7a-9a6085f37b1d)

## Задание 8

```
#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Использование: $0 /путь/к/каталогу <расширение>."
	exit 1
fi

directory="$1"
extension="$2"

if [ ! -d "$directory" ]; then
	echo "Ошибка: указанный каталог '$directory' не существует."
	exit 1
fi

shopt -s nullglob
files=("$directory"/*."$extension")

if [ ${#files[@]} -eq 0 ]; then
	echo "Ошибка: в указанном каталоге '$directory' нет файлов с расширением .'$extension'."
	exit 1
fi

archive_name="${directory%/}.tar"

tar -cvf "$archive_name" -C "$directory" ./*."$extension"

echo "Архив '$archive_name' успешно создан."
```
![image](https://github.com/user-attachments/assets/acbd3b98-e1c0-4035-beb0-341410c61723)

## Задание 9

```
#!/bin/bash

if [ "$#" -ne 2 ]; then
	echo "Использование: $0 <входной_файл> <выходной_файл>"
	exit 1
fi

input_file="$1"
output_file="$2"

if [ ! -f "$input_file" ]; then
	echo "Ошибка: '$input_file' не найден."
	exit 1
fi

sed 's/    /\t/g' "$input_file" > "$output_file"

echo "Заменено в файле: '$output_file'"
```
![image](https://github.com/user-attachments/assets/5e48972c-2154-4ba2-bfea-93aa40584567)

## Задание 10

```
#!/bin/bash

if [ "$#" -ne 1 ]; then
	echo "Использование: $0 /путь/к/каталогу."
	exit 1
fi

directory="$1"

if [ ! -d "$directory" ]; then
	echo: "Ошибка: указанный каталог '$directory' не существует."
	exit 1
fi

find "$directory" -type f -name "*.txt" -empty -exec basename {} \;
```
![image](https://github.com/user-attachments/assets/811f4ac9-c301-45c8-a43b-a96a2f8d9bfe)
