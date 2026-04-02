/**
 * 游戏版本信息 API
 */

import { request } from './request'


/**
 * 游戏版本信息
 */
export interface GameVersionInfo {
  game_name: string
  version: string
  update_time: string
  update_content?: string
  source_url?: string
}


/**
 * 支持的游戏信息
 */
export interface SupportedGame {
  code: string
  name: string
  platform: string
}


/**
 * 支持的游戏列表响应
 */
export interface SupportedGamesResponse {
  games: SupportedGame[]
}


/**
 * 获取指定游戏的最新版本
 */
export function getLatestVersion(game: string = 'honor_of_kings'): Promise<GameVersionInfo> {
  return request.get(`/game-version/latest?game=${game}`)
}


/**
 * 获取所有游戏的版本信息
 */
export function getAllVersions(): Promise<GameVersionInfo[]> {
  return request.get('/game-version/all')
}


/**
 * 获取支持的游戏列表
 */
export function getSupportedGames(): Promise<SupportedGamesResponse> {
  return request.get('/game-version/supported-games')
}
