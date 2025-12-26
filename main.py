import os
import asyncio
import csv
import pandas as pd
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application, MessageHandler, filters
from telegram import Update, BotCommand
from io import BytesIO
import matplotlib.pyplot as plt

user_files: dict[int, pd.DataFrame] = {}
async def set_dataset(update: Update, _context) -> None:
  message = update.message
  
  file = await message.document.get_file()
  file_buffer = BytesIO()
  await file.download_to_memory(file_buffer)
  file_buffer.seek(0)
  content = file_buffer.read(10)
  file_buffer.seek(0)
  df = pd.read_csv(file_buffer)
  user_files[update.effective_chat.id] = df
  await message.reply_text(str(df))

async def plot_scatter(update: Update, _context) -> None:
  message = update.message

  df = user_files[update.effective_chat.id] if update.effective_chat.id in user_files else None
  if df is None:
    await message.reply_text("no dataset specified")
    return
  
  plt.scatter(df["X"].values, df["Y"].values)
  plt.xlabel("X")
  plt.ylabel("Y")
  fig_buffer = BytesIO()
  plt.savefig(fig_buffer, format='png')
  fig_buffer.flush()
  fig_buffer.seek(0)

  await message.reply_document(fig_buffer, filename="scatter.png")

async def plot_hist(update: Update, _context) -> None:
  message = update.message

  df = user_files[update.effective_chat.id] if update.effective_chat.id in user_files else None
  if df is None:
    await message.reply_text("no dataset specified")
    return
  
  plt.hist(df["X"])
  plt.xlabel("X")
  fig_buffer = BytesIO()
  plt.savefig(fig_buffer, format='png')
  fig_buffer.flush()
  fig_buffer.seek(0)

  await message.reply_document(fig_buffer, filename="hist.png")

async def plot_heatmap(update: Update, _context) -> None:
  message = update.message

  df = user_files[update.effective_chat.id] if update.effective_chat.id in user_files else None
  if df is None:
    await message.reply_text("no dataset specified")
    return
  
  x, y, z = df["X"].values, df["Y"].values, df["Z"].values
  plt.tricontourf(x, y, z, levels=100, cmap="viridis")
  plt.colorbar(label="z value")
  plt.xlabel("x")
  plt.ylabel("y")

  fig_buffer = BytesIO()
  plt.savefig(fig_buffer, format='png')
  fig_buffer.flush()
  fig_buffer.seek(0)

  await message.reply_document(fig_buffer, filename="heatmap.png")


def setup_commands(app: Application) -> None:
  app.add_handler(MessageHandler(
    filters.CaptionRegex(r'^/set_dataset$') & filters.Document.TEXT,
    set_dataset
  ))
  # app.bot.set_my_commands([
  #   BotCommand("set_dataset [attached_file]", "set a dataset"),
  #   BotCommand("plot_scatter", "plot a scatter"),
  #   BotCommand("plot_hist", "plot a histogram"),
  #   BotCommand("plot_heatmap", "plot a heatmap")
  # ])
  app.add_handler(CommandHandler("plot_scatter", plot_scatter))
  app.add_handler(CommandHandler("plot_hist", plot_hist))
  app.add_handler(CommandHandler("plot_heatmap", plot_heatmap))

def main():
  load_dotenv()
  BOT_TOKEN = os.environ["BOT_TOKEN"]
  app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
  )

  setup_commands(app)
  
  app.run_polling()


if __name__ == "__main__":
  main()